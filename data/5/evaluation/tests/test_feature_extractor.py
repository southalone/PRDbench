import pytest
import os
import sys
from PIL import Image

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from feature_extractor import extract_dominant_colors, extract_texture_features, analyze_image_features

def test_dominant_colors_extraction():
    """测试主色调提取功能"""
    # Create a test image with known colors
    image = Image.new('RGB', (100, 100), color='red')
    
    # Save to temporary file
    temp_path = os.path.join(os.path.dirname(__file__), 'temp_color_test_image.jpg')
    image.save(temp_path, format='JPEG')
    
    try:
        # Extract dominant colors
        colors = extract_dominant_colors(temp_path)
        
        # Check that we got results
        assert len(colors) > 0
        
        # Check that the dominant color is red-like (starts with #e or #f)
        dominant_color, percentage = colors[0]
        # Red should be #ff0000, but with color quantization it might be slightly different
        assert dominant_color.startswith('#e') or dominant_color.startswith('#f')
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_texture_extraction():
    """测试纹理特征提取功能"""
    # Create a test image with a smooth texture
    smooth_image = Image.new('L', (100, 100), color=128)  # Gray image
    
    # Save to temporary file
    temp_path = os.path.join(os.path.dirname(__file__), 'temp_texture_test_image.jpg')
    smooth_image.save(temp_path, format='JPEG')
    
    try:
        # Extract texture features
        texture = extract_texture_features(temp_path)
        
        # For a uniform image, we expect "细腻" (smooth) texture
        assert texture == "细腻"
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_analyze_image_features():
    """测试整体图像特征分析功能"""
    # Create a test image
    image = Image.new('RGB', (100, 100), color='blue')
    
    # Save to temporary file
    temp_path = os.path.join(os.path.dirname(__file__), 'temp_analysis_test_image.jpg')
    image.save(temp_path, format='JPEG')
    
    try:
        # Analyze features
        features = analyze_image_features(temp_path)
        
        # Check that we got both dominant colors and texture
        assert 'dominant_colors' in features
        assert 'texture' in features
        
        # Check that dominant colors exist
        assert len(features['dominant_colors']) > 0
        
        # Check that texture is either "细腻" or "粗糙"
        assert features['texture'] in ["细腻", "粗糙"]
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    pytest.main([__file__])