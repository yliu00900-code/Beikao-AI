import contextlib
import io
import tempfile
import unittest
from unittest import mock

from recognition.ocr import available_languages, select_language, recognize


class SelectLanguageTests(unittest.TestCase):
    def test_available_languages_parses_tesseract_output(self):
        result = mock.Mock(returncode=0, stdout='List of available languages in "tessdata" (2):\neng\nchi_sim\n', stderr='')
        with mock.patch('recognition.ocr.shutil.which', return_value='/usr/bin/tesseract'), \
             mock.patch('recognition.ocr.subprocess.run', return_value=result):
            self.assertEqual(available_languages(), ['eng', 'chi_sim'])

    def test_select_chinese_and_english_when_both_installed(self):
        self.assertEqual(select_language(None, ["eng", "chi_sim"]), ("chi_sim+eng", None))

    def test_fallback_to_english_warns(self):
        language, warning = select_language(None, ["eng"])
        self.assertEqual(language, "eng")
        self.assertIn("中文语言包", warning)

    def test_explicit_missing_language_fails_instead_of_silent_fallback(self):
        with self.assertRaisesRegex(RuntimeError, "chi_sim"):
            select_language("chi_sim+eng", ["eng"])

    def test_no_languages_fails(self):
        with self.assertRaisesRegex(RuntimeError, "没有可用语言包"):
            select_language(None, [])


class RecognizeTests(unittest.TestCase):
    def test_local_image_does_not_request_adb_screenshot(self):
        with tempfile.NamedTemporaryFile(suffix=".png") as image_file:
            mocked = mock.Mock(return_value=mock.Mock(returncode=0, stdout="Test OCR\n", stderr=""))
            with mock.patch("recognition.ocr.available_languages", return_value=["eng"]), \
                 mock.patch("recognition.ocr.take_screenshot") as screenshot, \
                 mock.patch("recognition.ocr.subprocess.run", mocked), \
                 contextlib.redirect_stderr(io.StringIO()) as warnings:
                result = recognize(image_file.name)
            screenshot.assert_not_called()
            self.assertEqual(result, "Test OCR")
            command = mocked.call_args.args[0]
            self.assertIn(image_file.name, command)
            self.assertEqual(command[-1], "eng")
            self.assertIn("中文识别准确度", warnings.getvalue())

    def test_missing_local_image_is_reported(self):
        with mock.patch("recognition.ocr.available_languages", return_value=["eng"]):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaisesRegex(RuntimeError, "图片文件不存在"):
                    recognize("/definitely/missing/image.png")

    def test_language_option_passes_to_tesseract(self):
        with tempfile.NamedTemporaryFile(suffix=".png") as image_file:
            mocked = mock.Mock(return_value=mock.Mock(returncode=0, stdout="中文", stderr=""))
            with mock.patch("recognition.ocr.available_languages", return_value=["chi_sim", "eng"]), \
                 mock.patch("recognition.ocr.subprocess.run", mocked):
                result = recognize(image_file.name, "chi_sim+eng")
            self.assertEqual(result, "中文")
            self.assertEqual(mocked.call_args.args[0][-1], "chi_sim+eng")


if __name__ == "__main__":
    unittest.main()
