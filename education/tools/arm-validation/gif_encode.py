"""Bounded JPEG-to-GIF codec; no browser, model or numerical imports."""
import io, hashlib
from contextlib import contextmanager, closing
from PIL import Image
@contextmanager
def quantized_frame(path,palette):
    with closing(Image.open(path)) as image, closing(image.convert('RGB')) as rgb:
        with closing(rgb.quantize(palette=palette,dither=Image.Dither.NONE)) as frame:
            yield frame
def palette_frames(paths,palette):
    # Pillow copies each yielded frame before requesting the next one. Keep
    # only that current source, rather than a second complete frame inventory.
    for path in paths:
        with quantized_frame(path,palette) as frame:yield frame
def encode_shared_palette(paths):
    if not 1<=len(paths)<=34:raise ValueError('GIF frame ceiling')
    with closing(Image.new('RGB',(160,120*len(paths)))) as atlas:
        for i,path in enumerate(paths):
            if path.stat().st_size>262144:raise ValueError('JPEG byte ceiling')
            with closing(Image.open(path)) as image:
                if image.size!=(960,720) or image.format!='JPEG' or image.quantization[0][0]!=5:raise ValueError('JPEG85 geometry/quantization')
                with closing(image.convert('RGB')) as rgb, closing(rgb.resize((160,120))) as thumb:atlas.paste(thumb,(0,120*i))
        palette=atlas.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
    with closing(palette):
        palette_bytes=bytes(palette.getpalette())
        with quantized_frame(paths[0],palette) as first, io.BytesIO() as output:
            remaining=palette_frames(paths[1:],palette)
            try:first.save(output,format='GIF',save_all=True,append_images=remaining,palette=palette_bytes,optimize=False,duration=500,loop=0,disposal=2)
            finally:remaining.close()
            data=output.getvalue()
        if len(data)>8388608:raise ValueError('GIF byte ceiling')
        with io.BytesIO(data) as buffer, closing(Image.open(buffer)) as image:
            if image.n_frames!=len(paths) or image.size!=(960,720):raise ValueError('GIF frame/resolution gate')
            for i,path in enumerate(paths):
                image.seek(i)
                with quantized_frame(path,palette) as frame, closing(image.convert('RGB')) as decoded, closing(frame.convert('RGB')) as expected:
                    if decoded.tobytes()!=expected.tobytes():raise ValueError('GIF palette/frame decode gate')
    return data,dict(globalPaletteSHA256=hashlib.sha256(palette_bytes).hexdigest(),paletteMethod='Shared all-frame JPEG thumbnail median-cut, 256 colors; no dithering',frameDurationMilliseconds=500,frames=len(paths),decodedFramesMatch=True,interpolation=False)
