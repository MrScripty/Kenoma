"""Decoded-image ownership and lazy encoding; synthetic codec bytes only."""
import io,pathlib,sys,tempfile,unittest
from contextlib import contextmanager
from unittest.mock import patch
from PIL import Image,ImageDraw
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-validation'))
import gif_encode as codec,render_worker as worker
class LifetimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='kr-lifetime-',dir='/tmp');self.root=pathlib.Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def jpg(self,i,size=(960,720)):
        path=self.root/f'{i}.jpg'
        with Image.new('RGB',size,'#15202a') as image:
            draw=ImageDraw.Draw(image);draw.rectangle((40+i*7,100,300+i*7,650),fill='#d87575');draw.text((18,18),f'SYNTHETIC TEST {i} — NO SIMULATION',fill='white');image.save(path,quality=85)
        return path
    def assert_closed(self,image):
        with self.assertRaises(ValueError):image.getpixel((0,0))
    def test_jpeg_validation_closes_decoded_image_and_buffer_before_return_or_refusal(self):
        opened=[];buffers=[];original=Image.open
        def track(buffer):
            image=original(buffer);opened.append(image);buffers.append(buffer);return image
        with patch.object(worker.Image,'open',side_effect=track):
            worker.validate_jpeg85(self.jpg(0).read_bytes())
            with self.assertRaisesRegex(ValueError,'quantization'):worker.validate_jpeg85(self.jpg(1,size=(100,100)).read_bytes())
        for image,buffer in zip(opened,buffers):self.assert_closed(image);self.assertTrue(buffer.closed)
    def test_jpeg_load_failure_closes_both_resources(self):
        original=Image.open;opened=[];buffers=[]
        def broken(buffer):
            image=original(buffer);opened.append(image);buffers.append(buffer);image.load=lambda:(_ for _ in ()).throw(OSError('damaged decode'));return image
        with patch.object(worker.Image,'open',side_effect=broken):
            with self.assertRaisesRegex(OSError,'damaged decode'):worker.validate_jpeg85(self.jpg(0).read_bytes())
        # close() clears the imaging core even when load() itself failed.
        with self.assertRaises(ValueError):opened[0].im
        self.assertTrue(buffers[0].closed)
    def test_lazy_generator_releases_previous_and_closes_on_early_exit(self):
        paths=[self.jpg(i) for i in range(3)]
        with Image.new('P',(1,1)) as palette:
            palette.putpalette([i for i in range(256) for _ in range(3)])
            generator=codec.palette_frames(paths,palette)
            first=next(generator);first.getpixel((0,0))
            second=next(generator);self.assert_closed(first);second.getpixel((0,0))
            generator.close();self.assert_closed(second)
    def test_max34_codec_retains_at_most_two_source_palette_frames(self):
        paths=[self.jpg(i) for i in range(34)];original=codec.quantized_frame;active=0;peak=0;closed=[]
        @contextmanager
        def tracked(path,palette):
            nonlocal active,peak
            with original(path,palette) as frame:
                active+=1;peak=max(peak,active)
                try:yield frame
                finally:active-=1;closed.append(frame)
        with patch.object(codec,'quantized_frame',tracked):data,receipt=codec.encode_shared_palette(paths)
        self.assertEqual(active,0);self.assertEqual(peak,2);self.assertEqual(len(closed),68)
        for frame in closed:self.assert_closed(frame)
        self.assertEqual(receipt['frames'],34);self.assertTrue(receipt['decodedFramesMatch'])
        with io.BytesIO(data) as buffer, Image.open(buffer) as image:
            self.assertEqual(image.n_frames,34)
            for i in range(34):image.seek(i);self.assertEqual(image.info['duration'],500);self.assertEqual(image.disposal_method,2)
    def test_encoding_failure_closes_current_generator_and_first_frame(self):
        paths=[self.jpg(i) for i in range(3)];original=codec.quantized_frame;frames=[]
        @contextmanager
        def tracked(path,palette):
            with original(path,palette) as frame:frames.append(frame);yield frame
        def fail_save(first,*args,**kwargs):
            next(kwargs['append_images']);raise OSError('injected writer failure')
        with patch.object(codec,'quantized_frame',tracked),patch.object(Image.Image,'save',fail_save):
            with self.assertRaisesRegex(OSError,'injected writer'):codec.encode_shared_palette(paths)
        self.assertEqual(len(frames),2)
        for frame in frames:self.assert_closed(frame)
if __name__=='__main__':unittest.main()
