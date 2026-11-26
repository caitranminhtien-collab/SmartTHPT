"""Original practice questions, generated from elementary math templates."""
import json
from pathlib import Path

TOPICS = ['Ứng dụng đạo hàm', 'Nguyên hàm – tích phân', 'Hình học Oxyz', 'Xác suất có điều kiện', 'Thống kê mẫu ghép nhóm', 'Vectơ trong không gian']

def make_questions():
    import random
    rng = random.Random(42)
    rows = []
    def add(topic, prompt, correct, wrong, explanation, level='Cơ bản'):
        opts = [str(correct), *map(str, wrong)]
        assert len(set(opts)) == 4, (prompt, opts)
        rng.shuffle(opts)
        rows.append(dict(topic=topic, prompt=prompt, options=opts, answer=opts.index(str(correct)), explanation=explanation, difficulty=level, source='Tự biên soạn (mẫu thuật toán)', grade=12, subject='Toán'))
    for a in range(1, 6):
        add(TOPICS[0], f'Hàm số f(x) = x² − {2*a}x + 1 đạt cực tiểu tại x bằng bao nhiêu?', a, [-a, 2*a, 2*a+1], f'f′(x) = 2x − {2*a}. Giải f′(x) = 0 được x = {a}. Vì hệ số x² dương nên đây là điểm cực tiểu.')
        add(TOPICS[0], f'Cho f(x) = x³ + {a}x. Giá trị f′(2) bằng bao nhiêu?', 12+a, [6+a, 8+a, 14+a], f'f′(x) = 3x² + {a}; thay x = 2 được {12+a}.')
        add(TOPICS[1], f'Tính tích phân từ 0 đến {a} của hàm số 2x.', a*a, [a*a+1, a*a+2, a*a+3], f'Nguyên hàm của 2x là x². Thế cận được {a}² − 0² = {a*a}.')
        add(TOPICS[1], f'Cho F′(x) = {a} và F(0) = 2. Tính F(3).', 3*a+2, [3*a, 3*a+1, 3*a+3], f'F(x) = {a}x + C. F(0) = 2 nên C = 2. F(3) = {3*a+2}.', 'Vận dụng')
        add(TOPICS[2], f'Trong hệ tọa độ Oxyz, cho A({a}; 2; 3), B({a+4}; 2; 3). Tính độ dài đoạn thẳng AB.', 4, [2, 5, 16], 'AB = √(4² + 0² + 0²) = 4.')
        add(TOPICS[2], f'Mặt phẳng x + 2y + 3z − {a} = 0 có một vectơ pháp tuyến là vectơ nào?', '(1; 2; 3)', ['(2; 1; 3)', '(0; 2; 3)', '(1; 3; 2)'], 'Với mặt phẳng Ax + By + Cz + D = 0, vectơ pháp tuyến là (A; B; C).')
        add(TOPICS[3], f'Một hộp có {a} bi đỏ và {a+2} bi xanh. Rút liên tiếp 2 bi không hoàn lại. Biết bi đầu màu đỏ, xác suất bi thứ hai màu xanh là?', f'{a+2}/{2*a+1}', [f'{a}/{2*a+1}', f'{a+2}/{2*a+2}', '0'], f'Sau khi rút bi đỏ còn {2*a+1} bi, trong đó {a+2} bi xanh. Xác suất có điều kiện bằng {a+2}/{2*a+1}.', 'Vận dụng')
        add(TOPICS[3], f'Cho P(B) = 0,5 và P(A ∩ B) = 0,{a}. Tính P(A | B).', f'{a}/5', [f'{a}/10', f'{a}/20', '0'], f'P(A | B) = P(A ∩ B)/P(B) = ({a}/10)/(1/2) = {a}/5.')
        add(TOPICS[4], f'Nhóm [{10*a}; {10*a+10}) của mẫu số liệu ghép nhóm có giá trị đại diện là bao nhiêu?', 10*a+5, [10*a, 10*a+10, 10*a+1], 'Giá trị đại diện là trung điểm của khoảng nhóm.')
        add(TOPICS[4], f'Mẫu số liệu ghép nhóm có hai nhóm [0; 2) và [2; 4), tần số lần lượt {a} và {a}. Tính số trung bình gần đúng.', 2, [1, 3, 4], f'Giá trị đại diện là 1 và 3. Trung bình = ({a}×1 + {a}×3)/({2*a}) = 2.')
        add(TOPICS[5], f'Cho hai vectơ u = ({a}; 1; 0) và v = (2; 0; 1). Tích vô hướng u · v bằng bao nhiêu?', 2*a, [2*a+1, a, 2*a+2], f'u · v = {a}×2 + 1×0 + 0×1 = {2*a}.')
        add(TOPICS[5], f'Cho vectơ u = ({a}; 2; 1), v = (1; 3; 2). Tọa độ vectơ u + v là?', f'({a+1}; 5; 3)', [f'({a}; 5; 3)', f'({a+1}; 6; 3)', f'({a+1}; 5; 2)'], 'Cộng các thành phần tọa độ tương ứng của hai vectơ.')
    return rows

if __name__ == '__main__':
    p=Path(__file__).resolve().parents[1]/'data'/'questions.json'
    p.write_text(json.dumps(make_questions(), ensure_ascii=False, indent=2),encoding='utf-8')
