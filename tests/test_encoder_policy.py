import os
import unittest
from unittest.mock import patch

from scripts import common


class EncoderPolicyTests(unittest.TestCase):
    def setUp(self):
        common._CACHED_VIDEO_ENCODER = None
        common._CACHED_ENCODER_CONTEXT = None
        self._env_backup = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env_backup)
        common._CACHED_VIDEO_ENCODER = None
        common._CACHED_ENCODER_CONTEXT = None

    @patch('scripts.common._is_encoder_usable')
    @patch('scripts.common._load_available_encoders')
    def test_auto_picks_first_usable_hw_then_cpu(self, mock_available, mock_usable):
        os.environ['CA_ENCODER_POLICY'] = 'auto'
        os.environ['CA_ENCODER_PRIORITY'] = 'h264_nvenc,h264_qsv,libx264'

        mock_available.return_value = {'h264_nvenc', 'h264_qsv', 'libx264'}
        mock_usable.side_effect = lambda enc: enc == 'h264_qsv'

        selected = common._detect_best_video_encoder()
        self.assertEqual(selected, 'h264_qsv')

    @patch('scripts.common._is_encoder_usable')
    @patch('scripts.common._load_available_encoders')
    def test_auto_falls_back_to_cpu(self, mock_available, mock_usable):
        os.environ['CA_ENCODER_POLICY'] = 'auto'
        mock_available.return_value = {'h264_nvenc', 'libx264'}
        mock_usable.side_effect = lambda enc: enc == 'libx264'

        selected = common._detect_best_video_encoder()
        self.assertEqual(selected, 'libx264')

    @patch('scripts.common._is_encoder_usable')
    @patch('scripts.common._load_available_encoders')
    def test_strict_gpu_raises_without_usable_hw(self, mock_available, mock_usable):
        os.environ['CA_ENCODER_POLICY'] = 'strict_gpu'
        mock_available.return_value = {'h264_nvenc', 'libx264'}
        mock_usable.return_value = False

        with self.assertRaises(RuntimeError):
            common._detect_best_video_encoder()

    @patch('scripts.common._is_encoder_usable')
    @patch('scripts.common._load_available_encoders')
    def test_cpu_only_always_uses_libx264(self, mock_available, mock_usable):
        os.environ['CA_ENCODER_POLICY'] = 'cpu_only'
        mock_available.return_value = {'h264_nvenc', 'libx264'}
        mock_usable.return_value = True

        selected = common._detect_best_video_encoder()
        self.assertEqual(selected, 'libx264')
        mock_usable.assert_not_called()

    def test_priority_override_keeps_order_and_libx264(self):
        os.environ['CA_ENCODER_PRIORITY'] = 'h264_amf,h264_nvenc'
        self.assertEqual(
            common._get_encoder_priority(),
            ['h264_amf', 'h264_nvenc', 'libx264']
        )


if __name__ == '__main__':
    unittest.main()
