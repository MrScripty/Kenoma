"""Bounded JPEG-to-GIF codec; no browser, model or numerical imports."""
import io, hashlib
from PIL import Image
def encode_shared_palette(paths):
    if not 1<=len(paths)<=34:raise ValueError('GIF frame ceiling')
    thumbs=[]
    for path in paths:
        if path.stat().st_size>262144:raise ValueError('JPEG byte ceiling')
        with Image.open(path) as image:
            if image.size!=(960,720) or image.format!='JPEG' or image.quantization[0][0]!=5:raise ValueError('JPEG85 geometry/quantization')
            thumbs.append(image.convert('RGB').resize((160,120)))
    atlas=Image.new('RGB',(160,120*len(thumbs)))
    for i,image in enumerate(thumbs):atlas.paste(image,(0,120*i))
    palette=atlas.quantize(colors=256,method=Image.Quantize.MEDIANCUT);palette_bytes=bytes(palette.getpalette());frames=[]
    for path in paths:
        with Image.open(path) as image:frames.append(image.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE))
    output=io.BytesIO();frames[0].save(output,format='GIF',save_all=True,append_images=frames[1:],palette=palette_bytes,optimize=False,duration=500,loop=0,disposal=2);data=output.getvalue()
    if len(data)>8388608:raise ValueError('GIF byte ceiling')
    with Image.open(io.BytesIO(data)) as image:
        if image.n_frames!=len(paths) or image.size!=(960,720):raise ValueError('GIF frame/resolution gate')
        for i,frame in enumerate(frames):
            image.seek(i)
            if image.convert('RGB').tobytes()!=frame.convert('RGB').tobytes():raise ValueError('GIF palette/frame decode gate')
    return data,dict(globalPaletteSHA256=hashlib.sha256(palette_bytes).hexdigest(),paletteMethod='Shared all-frame JPEG thumbnail median-cut, 256 colors; no dithering',frameDurationMilliseconds=500,frames=len(paths),decodedFramesMatch=True,interpolation=False)
