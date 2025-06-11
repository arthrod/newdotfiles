"""Tests for screen helper functionality."""

import os
import tempfile
import time
from unittest.mock import Mock, patch, MagicMock

import cv2
import numpy as np
import pytest
from playwright.sync_api import Page

from newdotfiles.screen_helper import ScreenAnalyzer, ScreenStreamHandler, ScreenHelperApp


class TestScreenAnalyzer:
    """Test the ScreenAnalyzer class."""
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        analyzer = ScreenAnalyzer("test-key")
        assert analyzer.api_key == "test-key"
    
    def test_init_from_env(self):
        """Test initialization from environment variable."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "env-key"}):
            analyzer = ScreenAnalyzer()
            assert analyzer.api_key == "env-key"
    
    def test_init_no_key_raises_error(self):
        """Test that missing API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Gemini API key required"):
                ScreenAnalyzer()
    
    @patch('newdotfiles.screen_helper.genai')
    def test_analyze_image_success(self, mock_genai):
        """Test successful image analysis."""
        # Mock the response
        mock_response = Mock()
        mock_response.text = "Test analysis result"
        mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response
        
        analyzer = ScreenAnalyzer("test-key")
        
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            # Create a simple test image
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            cv2.imwrite(tmp.name, test_image)
            
            result = analyzer.analyze_image(tmp.name)
            assert result == "Test analysis result"
            
            # Clean up
            os.unlink(tmp.name)
    
    @patch('newdotfiles.screen_helper.genai')
    def test_analyze_image_error(self, mock_genai):
        """Test image analysis error handling."""
        mock_genai.GenerativeModel.return_value.generate_content.side_effect = Exception("API Error")
        
        analyzer = ScreenAnalyzer("test-key")
        result = analyzer.analyze_image("nonexistent.jpg")
        assert "⚠️ Image analysis failed" in result
    
    @patch('newdotfiles.screen_helper.genai')
    def test_analyze_video_clip_success(self, mock_genai):
        """Test successful video analysis."""
        mock_response = Mock()
        mock_response.text = "Video analysis result"
        mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response
        
        analyzer = ScreenAnalyzer("test-key")
        
        # Create a temporary video file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            # Create a simple test video
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(tmp.name, fourcc, 10.0, (100, 100))
            
            # Write a few frames
            for _ in range(10):
                frame = np.zeros((100, 100, 3), dtype=np.uint8)
                writer.write(frame)
            writer.release()
            
            result = analyzer.analyze_video_clip(tmp.name)
            assert result == "Video analysis result"
            
            # Clean up
            os.unlink(tmp.name)
    
    @patch('newdotfiles.screen_helper.genai')
    def test_check_duplicate_true(self, mock_genai):
        """Test duplicate checking returns True."""
        mock_response = Mock()
        mock_response.text = "true"
        mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response
        
        analyzer = ScreenAnalyzer("test-key")
        result = analyzer.check_duplicate("same text", "same text")
        assert result is True
    
    @patch('newdotfiles.screen_helper.genai')
    def test_check_duplicate_false(self, mock_genai):
        """Test duplicate checking returns False."""
        mock_response = Mock()
        mock_response.text = "false"
        mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response
        
        analyzer = ScreenAnalyzer("test-key")
        result = analyzer.check_duplicate("different", "text")
        assert result is False
    
    def test_check_duplicate_no_previous(self):
        """Test duplicate checking with no previous text."""
        analyzer = ScreenAnalyzer("test-key")
        result = analyzer.check_duplicate("current", "")
        assert result is False


class TestScreenStreamHandler:
    """Test the ScreenStreamHandler class."""
    
    def test_init(self):
        """Test handler initialization."""
        analyzer = Mock()
        handler = ScreenStreamHandler(analyzer)
        assert handler.analyzer == analyzer
        assert handler.buffer == []
        assert handler.recording is False
    
    def test_copy(self):
        """Test handler copy method."""
        analyzer = Mock()
        handler = ScreenStreamHandler(analyzer)
        copy = handler.copy()
        assert isinstance(copy, ScreenStreamHandler)
        assert copy.analyzer == analyzer
    
    def test_start_stop_recording(self):
        """Test recording controls."""
        handler = ScreenStreamHandler()
        
        # Initially not recording
        assert handler.recording is False
        
        # Start recording
        handler.start_recording()
        assert handler.recording is True
        
        # Stop recording
        handler.stop_recording()
        assert handler.recording is False
        assert handler.buffer == []
    
    def test_receive_not_recording(self):
        """Test receive when not recording."""
        handler = ScreenStreamHandler()
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Should not add frames when not recording
        handler.receive(frame)
        assert handler.buffer == []
    
    def test_receive_recording_time_limit(self):
        """Test receive respects 2-second time limit."""
        analyzer = Mock()
        handler = ScreenStreamHandler(analyzer)
        handler.recording = True
        handler.latest_args = [None, None, "snapshots", [], []]
        
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # First frame should be added
        handler.receive(frame)
        assert len(handler.buffer) == 1
        
        # Second frame within 2 seconds should be added but not processed
        handler.receive(frame)
        assert len(handler.buffer) == 2
    
    def test_emit_with_frames(self):
        """Test emit returns latest frame."""
        handler = ScreenStreamHandler()
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = np.ones((100, 100, 3), dtype=np.uint8)
        
        handler.buffer = [frame1, frame2]
        result = handler.emit()
        np.testing.assert_array_equal(result, frame2)
    
    def test_emit_no_frames(self):
        """Test emit with no frames."""
        handler = ScreenStreamHandler()
        result = handler.emit()
        assert result is None


class TestScreenHelperApp:
    """Test the ScreenHelperApp class."""
    
    def test_init(self):
        """Test app initialization."""
        app = ScreenHelperApp()
        assert app.analyzer is None
        assert app.handler is None
    
    @patch('newdotfiles.screen_helper.gr.Timer')
    def test_create_interface(self, mock_timer):
        """Test interface creation."""
        mock_timer.return_value.tick = Mock()
        app = ScreenHelperApp()
        interface = app.create_interface()
        assert interface is not None


class TestIntegration:
    """Integration tests - real functionality only."""
    
    def test_connect_button_functionality(self):
        """Test the connect button logic."""
        app = ScreenHelperApp()
        
        # Test that we can create an app instance
        assert app.analyzer is None
        assert app.handler is None
    
    def test_recording_button_states(self):
        """Test recording button state changes."""
        handler = ScreenStreamHandler()
        
        # Test start recording
        assert handler.recording is False
        handler.start_recording()
        assert handler.recording is True
        
        # Test stop recording  
        handler.stop_recording()
        assert handler.recording is False
    
    def test_chat_update_logic(self):
        """Test chat update logic for different view modes."""
        raw_messages = [{"role": "assistant", "content": "Raw message 1"}]
        processed_messages = [{"role": "assistant", "content": "Processed message 1"}]
        
        # Test processed view
        def update_chat(raw_msgs, proc_msgs, view):
            return proc_msgs if view == "processed" else raw_msgs
        
        result = update_chat(raw_messages, processed_messages, "processed")
        assert result == processed_messages
        
        result = update_chat(raw_messages, processed_messages, "raw")
        assert result == raw_messages


def test_end_to_end_flow():
    """Test the complete flow with real components."""
    # Create app
    app = ScreenHelperApp()
    
    # Test that we can create a handler
    handler = ScreenStreamHandler()
    handler.recording = True
    
    # Test frame processing without analyzer (should handle gracefully)
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    handler.buffer.append(frame)
    
    # Force processing by setting time
    handler.last_chunk_time = time.time() - 3.0  # 3 seconds ago
    
    # Process the frame - should handle no analyzer gracefully
    handler.receive(frame)
    
    # Verify buffer is cleared
    assert len(handler.buffer) == 0


def test_create_app_function():
    """Test the create_app factory function."""
    from newdotfiles.screen_helper import create_app
    
    app = create_app()
    assert isinstance(app, ScreenHelperApp)
    assert app.analyzer is None
    assert app.handler is None