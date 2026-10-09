"""Real codec bytes with synthetic drawn frames; no browser or model calls."""
import io,pathlib,sys,tempfile,unittest
from PIL import Image,ImageDraw
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-validation'))
from gif_encode import encode_shared_palette
class GifTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory(prefix='kenoma-gif-synthetic-',dir='/tmp');self.root=pathlib.Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def jpg(self,i,quality=85,size=(960,720)):
        p=self.root/f'{i}.jpg';im=Image.new('RGB',size,'#15202a');d=ImageDraw.Draw(im);d.rectangle((100+i*3,150,400+i*3,600),fill='#d87575');d.text((18,18),'SYNTHETIC TEST — NO SIMULATION',fill='white');d.text((18,60),f'Provisional solver fixture {i}; no accepted motion',fill='white');im.save(p,quality=quality);return p
    def test_actual_jpeg85_bytes_shared_palette_decoded_frames_count_and_dimensions(self):
        paths=[self.jpg(i) for i in range(3)];data,receipt=encode_shared_palette(paths);self.assertTrue(receipt['decodedFramesMatch']);self.assertFalse(receipt['interpolation']);self.assertEqual(receipt['frames'],3);self.assertEqual(len(receipt['globalPaletteSHA256']),64)
        with Image.open(io.BytesIO(data)) as im:self.assertEqual(im.n_frames,3);self.assertEqual(im.size,(960,720));self.assertEqual(im.info['duration'],500)
    def test_quality_dimension_nonjpeg_count_and_byte_damage(self):
        with self.assertRaisesRegex(ValueError,'ceiling'):encode_shared_palette([])
        with self.assertRaisesRegex(ValueError,'ceiling'):encode_shared_palette([self.root/'absent']*35)
        with self.assertRaisesRegex(ValueError,'quantization'):encode_shared_palette([self.jpg(1,quality=95)])
        with self.assertRaisesRegex(ValueError,'geometry'):encode_shared_palette([self.jpg(2,size=(100,100))])
        p=self.jpg(3);p.write_bytes(b'x'*262145)
        with self.assertRaisesRegex(ValueError,'byte ceiling'):encode_shared_palette([p])
        p=self.root/'not-jpeg.png';Image.new('RGB',(960,720)).save(p)
        with self.assertRaisesRegex(ValueError,'JPEG85'):encode_shared_palette([p])
    def test_repeated_frames_cannot_silently_drop_retained_snapshot_count(self):
        p=self.jpg(1)
        with self.assertRaisesRegex(ValueError,'frame/resolution'):encode_shared_palette([p,p])
if __name__=='__main__':unittest.main()
