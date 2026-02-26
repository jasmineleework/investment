# 全脚本 Python 化 + Skill-Local 迁移

## Stream 1: data-fetch scripts
- [x] 创建 `yahoo_fetch.py` (替代 yahoo-fetch.ts)
- [x] 创建 `sec_edgar_fetch.py` (替代 sec-edgar-fetch.sh)
- [x] 创建 `fred_fetch.py` (替代 fred-fetch.sh)
- [x] 创建 `data-fetch/scripts/requirements.txt`
- [x] 更新 `data-fetch/SKILL.md` 脚本调用

## Stream 2: valuation scripts
- [x] 创建 `calc_dcf.py` (替代 calc-dcf.ts)
- [x] 创建 `calc_wacc.py` (替代 calc-wacc.ts)
- [x] 创建 `valuation/scripts/requirements.txt`
- [x] 更新 `valuation/SKILL.md` 脚本调用

## Stream 3: cleanup (依赖 Stream 1+2)
- [x] 删除 `scripts/` 公共目录
- [x] 删除旧 bash 脚本
- [x] 更新 .gitignore

## 验证
- [x] 运行所有 Python 脚本验证
- [x] 确认旧文件已删除
- [x] grep 检查无残留引用
