import pytest
import sys
import os

# 将src目录添加到Python路径中，以便可以导入其中的模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from huffman import build_huffman_tree, generate_huffman_codes, Node

def test_build_huffman_tree():
    """
    测试 build_huffman_tree 函数是否能正确构建哈夫曼树。
    """
    freq_map = {'a': 5, 'b': 9, 'c': 12, 'd': 13, 'e': 16, 'f': 45}
    tree = build_huffman_tree(freq_map)
    assert isinstance(tree, Node)
    assert tree.freq == 100


def test_generate_huffman_codes():
    """
    测试 generate_huffman_codes 函数是否能正确生成哈夫曼编码。
    """
    freq_map = {'a': 5, 'b': 9, 'c': 12, 'd': 13, 'e': 16, 'f': 45}
    tree = build_huffman_tree(freq_map)
    codes = generate_huffman_codes(tree)
    
    # 验证特定字符的编码是否符合预期（基于标准哈夫曼编码规则）
    assert codes['f'] == '0'
    assert codes['c'] == '100'
    assert codes['d'] == '101'
    assert codes['a'] == '1100'
    assert codes['b'] == '1101'
    assert codes['e'] == '111'


def test_build_tree_with_insufficient_nodes():
    """
    测试 build_huffman_tree 函数在输入节点不足时是否抛出 ValueError。
    """
    with pytest.raises(ValueError):
        build_huffman_tree({'a': 1})

if __name__ == '__main__':
    pytest.main([__file__, '-v'])