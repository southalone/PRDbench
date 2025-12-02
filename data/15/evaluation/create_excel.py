
import pandas as pd

def create_expected_excel():
    data = {
        '题目': ['Git中的`git rebase`命令有什么作用？'],
        '选项': ['合并分支, 创建新分支, 修改提交历史, 删除分支'],
        '答案': ['修改提交历史'],
        '解析': ['STAR法则分析示例：(S)情境: 在什么情况下... (T)任务: 你的具体任务是... (A)行动: 你采取了哪些步骤... (R)结果: 最终的结果是...'],
        '能力维度': ['专业知识'],
        '难度': ['中级'],
        '题型': ['单选题']
    }
    df = pd.DataFrame(data)
    df.to_excel("C:\\Users\\wb_zhangyuan20\\Desktop\\CDT\\evaluation\\expected_question_bank.xlsx", index=False)

create_expected_excel()
