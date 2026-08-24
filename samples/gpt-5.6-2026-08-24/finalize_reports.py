#!/usr/bin/env python3
"""Fill the prose sections that compile_report.py intentionally leaves to the analyst."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MODEL = "OpenAI Codex (GPT-5.6)"
DATE = "2026-08-24"


def load(name):
    p = ROOT / name / "report.json"
    return p, json.loads(p.read_text(encoding="utf-8"))


def save(path, data):
    data["meta"]["model"] = MODEL
    data["meta"]["generated_at"] = DATE
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def uncertainty_rows(report, text):
    for row in report["high_compensation"]["rows"]:
        row["uncertainty"] = text


def xiaomi():
    p, r = load("xiaomi")
    uncertainty_rows(r, "职级与股权覆盖为模型估计；单桶人数和跨线概率均非公司披露")
    save(p, r)


def pdd():
    p, r = load("pdd")
    r["meta"]["entity_type"] = "开曼注册、NASDAQ 上市的外国私人发行人"
    r["meta"]["scope"] = "PDD Holdings 合并口径；中国平台与跨境业务合并建模，职能人数采用 20-F 披露"
    r["executive"]["diagnosis"] = "拼多多是极高利润、极精干且股权费用密集的组织：模型显示约四分之一员工可能跨过百万 TC，但完整雇员福利开支未披露，因此该比例只能作为暂定区间。"
    uncertainty_rows(r, "职能人数为披露；职级拆分、现金/股权比例和跨线概率为模型假设")
    r["talent_pnl"] = [
        {"profit_pool": "在线营销服务", "process": "推荐与广告排序", "role": "广告算法/商业化平台负责人", "dependency": "高", "why": "推断毛利最高，商家ROI与用户留存同时受排序系统影响"},
        {"profit_pool": "交易服务", "process": "全球履约与供应链编排", "role": "履约平台/供应链负责人", "dependency": "高", "why": "交易服务收入超过2,140亿元，履约和支付成本直接决定单位经济性"},
        {"profit_pool": "交易服务", "process": "支付与交易风控", "role": "支付、反欺诈与商家风险负责人", "dependency": "高", "why": "跨市场交易扩大了欺诈、合规和资金安全暴露"},
        {"profit_pool": "全集团", "process": "跨境监管响应", "role": "产品合规/公共政策负责人", "dependency": "高", "why": "不直接创造收入，但可能决定市场准入与业务连续性"},
    ]
    r["organization"] = [
        {"native": "产品开发 entry", "track": "IC", "scope": "任务/项目", "function": "产品与工程", "state": "IC1-IC2", "confidence": "低（公司未披露职级名称）"},
        {"native": "产品开发 mid", "track": "IC/M", "scope": "项目/团队", "function": "产品与工程", "state": "IC3-IC4/M1", "confidence": "中（薪酬样本校准）"},
        {"native": "senior", "track": "IC/M", "scope": "多团队/关键系统", "function": "全职能", "state": "IC5/M2-M3", "confidence": "低"},
        {"native": "director", "track": "M", "scope": "职能/业务线", "function": "全职能", "state": "M4-M5", "confidence": "低"},
        {"native": "高级副总裁/联席CEO", "track": "高管", "scope": "公司/业务群P&L", "function": "集团", "state": "E", "confidence": "高（官方履历）"},
    ]
    r["role_pay"] = [
        {"role": "推荐/广告排序算法负责人", "market": "220-500万", "economic": "300-900万", "internal": "180-500万", "defensible": "300-500万", "diagnostic": "重合；内部下沿存在留才压力"},
        {"role": "跨境履约与供应链平台负责人", "market": "180-420万", "economic": "250-800万", "internal": "160-450万", "defensible": "250-420万", "diagnostic": "经济上限显著高于内部带"},
        {"role": "支付与交易风控负责人", "market": "180-400万", "economic": "220-650万", "internal": "150-400万", "defensible": "220-400万", "diagnostic": "重合；风险暴露支持溢价"},
        {"role": "资深产品/算法工程师", "market": "90-180万", "economic": "100-240万", "internal": "90-190万", "defensible": "100-180万", "diagnostic": "百万线附近，是主要跨阈值状态"},
    ]
    r["career"] = {
        "internal_path": ["产品/工程骨干 → 资深负责人 → 高级副总裁", "高级副总裁 → 联席CEO → 联席董事长/联席CEO"],
        "external_path": ["其他电商平台资深工程师 → 资深产品开发", "跨境供应链/支付专家 → 关键平台负责人"],
        "first_threshold_state": "产品开发 mid 的上部或全职能 senior；是否跨线高度取决于股权年化价值",
        "promotion_tenure": "仅8条公开路径，样本不足以计算公司级晋升概率；公开高管路径通常跨3-5年",
        "senior_hire_mix": "最高管理层更偏内部培养，跨境供应链、合规和支付岗位更可能外部引进",
    }
    r["governance"] = [
        {"metric": "股份支付", "value": "FY2025 79.37亿元", "evidence": "2025 Form 20-F"},
        {"metric": "员工法定供款", "value": "FY2025 23.67亿元", "evidence": "20-F Note 19"},
        {"metric": "股份计划", "value": "2015期权计划与2018期权/RSU计划；未披露全体覆盖人数", "evidence": "20-F"},
        {"metric": "B类股份", "value": "截至2026-03-18无B类普通股流通", "evidence": "20-F share ownership"},
        {"metric": "合伙人提名权", "value": "相关章程条款修改需95%出席票赞成", "evidence": "SEC备案组织章程"},
    ]
    r["sensitivity"] = [
        "高级层人数±25%是百万TC人数的第一敏感项，预计使p50变化约900-1,300人。",
        "SBC按会计授予日价值还是报告日市值计量，可使senior/director年化股权区间变化20%-40%。",
        "完整雇员福利开支未披露，本样例以275亿元包络假设校准；该假设变化10%会重塑全部职级带。",
        "最需要的新证据是非高管股权覆盖人数、按职级现金薪酬中位数和境外员工地域分布。",
    ]
    r["evidence"] = [
        {"id": "A01", "source": "PDD Holdings 2025 Form 20-F", "date": "2026-04", "status": "披露", "supports": "员工、SBC、法定供款、股份计划和控制结构"},
        {"id": "A02", "source": "FY2025业绩公告", "date": "2026-03", "status": "披露", "supports": "收入、成本、利润和业务收入"},
        {"id": "A03", "source": "SEC备案组织章程", "date": "2023-02", "status": "披露", "supports": "PDD Partnership提名权与95%修订门槛"},
        {"id": "C01", "source": "Levels.fyi中国软件工程师样本", "date": "2026-08", "status": "校准", "supports": "产品开发TC量级"},
        {"id": "M01", "source": "本报告模型与50,000次蒙特卡洛", "date": "2026-08", "status": "模型", "supports": "跨阈值人数与分布"},
    ]
    r["charter"] = {
        "summary": [
            {"item": "法律/上市结构", "current": "开曼公司，NASDAQ: PDD，外国私人发行人", "historical": "2018年美国上市", "evidence": "20-F/组织章程"},
            {"item": "股份类别", "current": "截至2026-03-18仅A类普通股流通", "historical": "历史上A/B双层结构", "evidence": "20-F"},
            {"item": "董事提名控制", "current": "PDD Partnership保留执行董事任命及CEO提名相关权利", "historical": "相关条款自重述章程延续", "evidence": "原始组织章程"},
            {"item": "修改门槛", "current": "影响合伙人提名权的条款需95%出席票赞成", "historical": "高于普通特别决议门槛", "evidence": "原始组织章程"},
            {"item": "员工股权工具", "current": "2015期权计划及2018期权/RSU计划", "historical": "持续确认大额SBC", "evidence": "20-F"},
        ],
        "timeline": [
            {"date": "2018-07", "event": "NASDAQ上市", "economic": "员工期权获得上市流动性", "control": "双层股份与创始人控制", "status": "原始文件"},
            {"date": "2023-02", "event": "公司更名并重述章程", "economic": "集团品牌与跨境业务重组", "control": "合伙人提名权条款延续", "status": "原始文件"},
            {"date": "2025-12", "event": "赵佳臻任联席董事长", "economic": "供应链投资权重上升", "control": "内部治理角色扩大", "status": "官方公告"},
            {"date": "2026-03", "event": "B类普通股归零", "economic": "普通股经济权利统一", "control": "合伙人章程权利仍需单独分析", "status": "原始文件"},
        ],
    }
    save(p, r)


def dreame():
    p, r = load("dreame")
    r["meta"]["entity_type"] = "中国非上市民营科技与智能制造集团（集团边界为重建口径）"
    r["meta"]["scope"] = "核心经营主体及含工厂侧的集团用工口径；不把加盟渠道和外包人员计入"
    r["executive"]["diagnosis"] = "追觅呈现制造业宽底与核心技术尖塔并存的薪酬结构：约4%-6%员工可能跨过百万TC，但收入、员工边界、利润和股权价值均缺少审计锚点，因此只能作为暂定估算。"
    r["executive"]["metrics"][2]["value"] = "约39.6万 CNY（模型推断）"
    uncertainty_rows(r, "员工边界、职级结构、私股价值和跨线概率均为宽区间推断")
    r["talent_pnl"] = [
        {"profit_pool": "智能清洁", "process": "高速数字马达", "role": "电机技术负责人", "dependency": "极高", "why": "核心技术差异化与产品性能直接相关，替代周期长"},
        {"profit_pool": "智能清洁", "process": "SLAM/运动控制", "role": "算法与机器人平台负责人", "dependency": "高", "why": "决定导航、避障和复杂家庭场景体验"},
        {"profit_pool": "大家电与新物种", "process": "品类定义与量产", "role": "品类总经理、供应链负责人", "dependency": "高", "why": "新BU从概念到规模化的关键瓶颈"},
        {"profit_pool": "海外渠道与服务", "process": "区域渠道、合规与售后", "role": "海外区域负责人", "dependency": "高", "why": "全球化收入依赖本地渠道效率和售后能力"},
    ]
    r["organization"] = [
        {"native": "校招/初级研发", "track": "IC", "scope": "任务/项目", "function": "研发", "state": "IC1-IC2", "confidence": "中（官方招聘）"},
        {"native": "项目骨干/中级", "track": "IC/M", "scope": "项目/小团队", "function": "研发、产品", "state": "IC3/M1", "confidence": "低"},
        {"native": "资深专家/负责人", "track": "IC/M", "scope": "关键系统/多团队", "function": "研发、品类", "state": "IC4-IC5/M2", "confidence": "低"},
        {"native": "BU负责人", "track": "经营", "scope": "业务线P&L", "function": "产品、销售、制造", "state": "M3-M4", "confidence": "中（公开组织报道）"},
        {"native": "制造/服务一线", "track": "一线", "scope": "任务", "function": "工厂与售后", "state": "F1", "confidence": "低"},
    ]
    r["role_pay"] = [
        {"role": "高速数字马达技术负责人", "market": "120-260万", "economic": "160-450万", "internal": "100-240万", "defensible": "160-240万", "diagnostic": "内部上沿偏低，存在留才压力"},
        {"role": "SLAM/运动控制算法负责人", "market": "140-300万", "economic": "180-500万", "internal": "110-280万", "defensible": "180-280万", "diagnostic": "关键技术岗位需专项股权"},
        {"role": "智能清洁品类总经理", "market": "120-260万", "economic": "180-550万", "internal": "100-260万", "defensible": "180-260万", "diagnostic": "适合P&L挂钩奖金"},
        {"role": "海外区域渠道负责人", "market": "100-240万", "economic": "140-400万", "internal": "90-220万", "defensible": "140-220万", "diagnostic": "区域业绩与回款质量应共同计价"},
    ]
    r["career"] = {
        "internal_path": ["校招研发 → 项目骨干 → 资深专家/技术负责人", "成熟业务骨干 → 新BU负责人"],
        "external_path": ["同业资深研发 → 核心技术专家", "消费电子/家电高管 → 品类或海外区域负责人"],
        "first_threshold_state": "核心算法/电机资深专家或成熟BU负责人；普通中级岗位通常仍低于百万线",
        "promotion_tenure": "公开路径仅8条且公司强调结果导向，不能据此计算晋升概率；样本常见24-36个月跃迁",
        "senior_hire_mix": "基础技术更偏内部培养，新品类、汽车与海外经营更依赖外部引进",
    }
    r["governance"] = [
        {"metric": "章程状态", "value": "历史章程未公开，治理结构为重建", "evidence": "工商与媒体材料"},
        {"metric": "集团边界", "value": "母体、追觅创新、追觅梦创及大量生态BU并存", "evidence": "工商穿透报道"},
        {"metric": "员工股权", "value": "覆盖人数、授予价和归属条件未公开", "evidence": "检索未取得"},
        {"metric": "现金激励", "value": "2025年多次团队/个人奖金；年末全员黄金奖励", "evidence": "公司公开口径媒体报道"},
        {"metric": "晋升定价", "value": "创始人公开称外聘涨幅通常不超过20%，业绩后再提拔涨薪", "evidence": "21财经"},
    ]
    r["sensitivity"] = [
        "员工口径从核心白领约7,000到含工厂/生态18,539差异最大；本报告采用后者并扩大区间。",
        "高级研发人数±25%可使百万TC p50改变约250-450人。",
        "私股风险折价从70%降至40%会明显提高senior/director跨线概率，但不能把名义估值当现金。",
        "最需要的新证据是审计集团财务、社保口径员工数、股权激励参与人数及各BU独立融资条款。",
    ]
    r["evidence"] = [
        {"id": "B01", "source": "追觅科技官网", "date": "2026-08", "status": "披露", "supports": "成立、核心技术与产品边界"},
        {"id": "B02", "source": "高校就业网官方招聘材料", "date": "2023-2025", "status": "披露", "supports": "校招薪酬结构与研发岗位"},
        {"id": "C01", "source": "公司口径媒体报道", "date": "2025-2026", "status": "需核验", "supports": "收入、员工规模与现金奖励"},
        {"id": "C02", "source": "工商穿透与组织报道", "date": "2026-05", "status": "重建", "supports": "集团/BU治理结构"},
        {"id": "E01", "source": "招聘聚合薪资样本", "date": "2026-08", "status": "弱校准", "supports": "普通岗位薪酬量级"},
        {"id": "M01", "source": "本报告模型与50,000次蒙特卡洛", "date": "2026-08", "status": "模型", "supports": "跨阈值人数与分布"},
    ]
    r["charter"] = {
        "summary": [
            {"item": "法律实体", "current": "追觅科技（苏州）有限公司及相关经营主体", "historical": "2017年成立并多轮融资", "evidence": "工商/公司官网"},
            {"item": "章程状态", "current": "未取得现行章程原文", "historical": "股权和控制条款由工商变更与融资报道重建", "evidence": "reconstructed"},
            {"item": "集团架构", "current": "母体下设主营平台与生态投资平台", "historical": "2025-2026大量BU和生态主体扩张", "evidence": "工商穿透报道"},
            {"item": "创始人控制", "current": "创始人对战略、资本配置和关键人事具有高度影响", "historical": "公开报道称其持续增持", "evidence": "媒体重建，不等同章程原文"},
            {"item": "员工激励", "current": "现金奖金与即时奖励可观察，股权条款不透明", "historical": "校招材料披露3-6个月绩效奖金", "evidence": "官方招聘/公开报道"},
        ],
        "timeline": [
            {"date": "2017", "event": "公司成立", "economic": "智能清洁创业", "control": "创始团队控制", "status": "官方摘要"},
            {"date": "2021", "event": "C轮融资", "economic": "扩大全球化与研发投入", "control": "外部投资人进入", "status": "官方/媒体摘要"},
            {"date": "2025", "event": "品类和BU快速扩张", "economic": "从清洁电器走向全屋与新物种", "control": "集团边界复杂化", "status": "重建"},
            {"date": "2025-12", "event": "全员黄金与绩效奖励", "economic": "用即时现金激励绑定扩张结果", "control": "股权覆盖仍不透明", "status": "公开报道"},
        ],
    }
    save(p, r)


if __name__ == "__main__":
    xiaomi()
    pdd()
    dreame()
