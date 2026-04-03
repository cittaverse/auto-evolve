#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-001 样本生成脚本
生成 200 条叙事文本用于 Multi-Agent Scorer v0.6 效度验证

样本构成:
- 140 条 正常叙述 (70%)
- 40 条 边界案例 (20%) - L0 置信度<0.6 或评分 55-75 分特征
- 20 条 堆砌样本 (10%) - 关键词堆砌

输出：exp-001-samples.csv
"""

import csv
import random
from datetime import datetime

random.seed(42)  # 可复现

# ============== 叙事模板库 ==============

# 正常叙述模板 (高质量，细节丰富) - 扩展版
NORMAL_TEMPLATES = [
    {
        "theme": "童年记忆",
        "template": "我{age}岁那年，住在{place}。{sensory_detail1}。{daily_scene}。{specific_event}。{emotion1}。{friend_story}。{sensory_detail2}。{reflection}"
    },
    {
        "theme": "工作经历",
        "template": "{year}年，我在{workplace}工作。{daily_routine}。{colleague_story}。{specific_achievement}。{difficulty}。{resolution}。{feeling}。{present_comparison}"
    },
    {
        "theme": "家庭生活",
        "template": "{family_member}是个{description}的人。{memory1}。{detail1}。{memory2}。{detail2}。{emotion}。{present_reflection}。{legacy}"
    },
    {
        "theme": "重大事件",
        "template": "{year}年发生了{event}。{scene}。{action}。{people_involved}。{emotion1}。{immediate_impact}。{emotion2}。{long_term_impact}"
    },
    {
        "theme": "青春回忆",
        "template": "年轻时我最喜欢{activity}。{place_detail}。{person}。{sensory1}。{specific_memory}。{sensory2}。{nostalgia}。{contrast}"
    },
    {
        "theme": "迁徙经历",
        "template": "{year}年我们从{origin}搬到{destination}。{reason}。{journey}。{first_impression}。{difficulty}。{adaptation}。{memory}。{feeling}"
    },
    {
        "theme": "婚姻故事",
        "template": "我和{spouse}是{year}年认识的。{meeting_story}。{courtship}。{wedding}。{early_life}。{challenge}。{life_together}。{feeling_now}"
    },
    {
        "theme": "养育子女",
        "template": "{child}小时候特别{trait}。{memory1}。{detail1}。{challenge}。{how_handled}。{pride}。{present}。{reflection}"
    }
]

# 填充元素库
PLACES = ["杭州西湖边", "上海弄堂里", "北京四合院", "广州骑楼下", "成都老街区", "西安城墙根", "南京颐和路", "武汉江汉路"]
WORKPLACES = ["纺织厂", "钢铁厂", "供销社", "人民公社", "小学", "医院", "铁路局", "造船厂"]
FAMILY_MEMBERS = ["母亲", "父亲", "祖父", "祖母", "大哥", "大姐", "舅舅", "姑妈"]
YEARS = ["1965", "1972", "1978", "1983", "1987", "1990", "1995", "2000"]
EVENTS = ["改革开放", "高考恢复", "唐山地震", "奥运会", "香港回归", "非典", "汶川地震"]
ACTIVITIES = ["听收音机", "看电影", "打篮球", "下棋", "唱歌", "跳舞", "读书", "钓鱼"]

SENSORY_DETAILS = [
    "记得那天阳光特别好，照在青石板路上暖洋洋的",
    "空气中飘着饭菜的香味，是妈妈在做红烧肉",
    "听到远处传来自行车的铃声，叮铃铃的",
    "能闻到桂花香，院子里那棵老桂花树开花了",
    "记得手上的触感，粗糙的棉布衣服",
    "耳边是蝉鸣声，夏天特别热闹",
    "看到炊烟袅袅升起，知道该吃晚饭了",
    "能尝到井水的甜味，冰凉冰凉的"
]

EMOTIONS = [
    "那时候虽然穷，但心里特别踏实",
    "现在想起来，眼眶还是会湿",
    "那段日子苦是苦，但一家人在一起就开心",
    "每当想起这些，心里就暖暖的",
    "有时候做梦还会回到那个地方",
    "说起来都是几十年前的事了，但记得清清楚楚",
    "现在条件好了，但总觉得少了点什么",
    "那是一种说不清的滋味，又苦又甜"
]

SPECIFIC_EVENTS = [
    "有一次我偷拿了家里的粮票去买糖，被妈妈发现了，狠狠地批评了我一顿",
    "记得第一次领工资那天，给妈妈买了双新布鞋，她高兴得哭了",
    "那年冬天特别冷，我发高烧，父亲背着我走了十里山路去看医生",
    "高考放榜那天，我一大早就跑到学校去看，看到自己的名字时手都在抖",
    "结婚那天没有婚纱，就穿了件红衣服，请同事们吃了些糖果",
    "孩子出生那天，我在产房外走来走去，听到哭声那一刻眼泪就下来了"
]

REFLECTIONS = [
    "现在想想，那可能就是最简单的幸福吧",
    "人生就是这样，有苦有甜，都过来了",
    "这些经历塑造了今天的我，我不后悔",
    "有时候觉得，过去的事情就像昨天发生的一样",
    "那一代人都是这么过来的，不算什么",
    "现在跟年轻人讲这些，他们可能不太能理解"
]

# 边界案例模板 (细节模糊，逻辑略跳跃)
BOUNDARY_TEMPLATES = [
    "记得那时候...好像是在{place}吧。具体哪年记不清了，大概是{year}年左右。{vague_event}。{unclear_feeling}。反正就是那样过来了。",
    "{year}年发生了一些事。{unclear_description}。细节记不太清了，只记得{fragment}。{hesitation}。",
    "我在那个时候...嗯...就是{workplace}工作。每天做些什么呢？{vague_routine}。{pause}。总的来说还可以吧。",
    "说起{family_member}，印象不是很深了。{fuzzy_memory}。{uncertain}。可能那时候还小吧。",
    "{year}年，发生了很多事情。{mixed_events}。{confused}。现在想起来有些模糊了。",
    "那个地方...叫什么来着...{place}？对，是那里。{incomplete_story}。{trailing_off}。后来就...",
    "年轻时的事记得不太清楚了。{fragment}。{vague_connection}。大概就是这样的。",
    "我记得...让我想想...{vague_description}。{long_pause}。时间太久了，记不清了。"
]

VAGUE_EVENTS = [
    "反正就是每天上班下班，日子一天天过",
    "有些人和事，现在都记不太清了",
    "就是那些平常的事，没什么特别的",
    "大概就是工作、吃饭、睡觉这样",
    "说不上来具体发生了什么，就是过日子"
]

FRAGMENTS = [
    "好像有个冬天特别冷",
    "记得有一次去了什么地方",
    "有个人对我挺好的",
    "好像吃过一次特别好吃的东西",
    "有那么一段时间很忙"
]

# 堆砌样本模板 (明显关键词堆砌)
STUFFING_TEMPLATES = [
    # C1 堆砌 - 感官细节过度
    "我看到阳光，我听到鸟叫，我闻到花香，我看到妈妈，我听到声音，我闻到饭菜香，我看到桌子，我听到笑声，我闻到茶香，我看到窗户，我听到音乐，我闻到草香。",
    
    # C2 堆砌 - 外部实体过度
    "1985 年夏天，杭州西湖边，我和母亲、父亲、大哥、大姐、舅舅、姑妈、叔叔、阿姨一起去了北京、上海、广州、成都、西安、南京、武汉、苏州。",
    
    # C4 堆砌 - 情感词过度
    "我非常开心非常激动非常高兴非常快乐非常幸福非常满足非常欣慰非常感动非常温暖非常甜蜜非常愉快非常兴奋非常喜悦非常满足非常骄傲。",
    
    # C5 堆砌 - 信息密度异常
    "那天那天那天那天天那天那天天那天天那天天那天那天天那天天那天天那天天那天天那天天那天天那天天那天天那天天那天天那天天那天天。",
    
    # 混合堆砌
    "我看到 1985 年杭州西湖我很开心我听到母亲我很激动我闻到花香我很高兴我看到父亲我很快乐我听到笑声我很幸福我闻到茶香我很满足。"
]


def generate_normal_sample(template_idx=None):
    """生成正常叙述样本"""
    if template_idx is None:
        template_idx = random.randint(0, len(NORMAL_TEMPLATES) - 1)
    
    t = NORMAL_TEMPLATES[template_idx]
    
    # 随机填充 - 扩展版 (按模板类型分别处理)
    if t["theme"] == "童年记忆":
        text = t["template"].format(
            age=random.randint(6, 12),
            place=random.choice(PLACES),
            sensory_detail1=random.choice(SENSORY_DETAILS),
            sensory_detail2=random.choice(SENSORY_DETAILS),
            daily_scene="邻居家的孩子们在巷子里追逐打闹，大人们坐在门口聊天择菜",
            specific_event=random.choice(SPECIFIC_EVENTS),
            emotion1=random.choice(EMOTIONS),
            friend_story="有个好朋友叫小明，我们经常一起上学，路上会捉知了、摸鱼",
            reflection=random.choice(REFLECTIONS)
        )
    elif t["theme"] == "工作经历":
        text = t["template"].format(
            year=random.choice(YEARS),
            workplace=random.choice(WORKPLACES),
            daily_routine="每天早上六点起床，骑自行车去厂里，八点钟开始工作，中午在食堂吃饭，下午五点下班",
            colleague_story="有个同事叫老王，对我特别好，经常帮我带早饭，有时候还借我粮票",
            specific_achievement="后来当了班组长，管十几个人，年底还得了先进工作者",
            difficulty="那时候条件艰苦，冬天手都冻裂了，夏天热得睡不着",
            resolution="但大家都咬牙坚持，互相帮衬着过日子",
            feeling="那段日子虽然累，但很充实，同事们关系也好",
            present_comparison="现在条件好了，但总觉得少了点什么"
        )
    elif t["theme"] == "家庭生活":
        text = t["template"].format(
            family_member=random.choice(FAMILY_MEMBERS),
            description="特别勤劳善良，一辈子没跟红过脸",
            memory1="记得有一次我生病，她照顾了我整整一周",
            detail1="每天天不亮就起来给我熬粥，还要上班",
            memory2="还有一次我考试没考好，她没骂我，反而鼓励我下次努力",
            detail2="那天晚上她陪我复习到很晚，自己却累得睡着了",
            emotion=random.choice(EMOTIONS),
            present_reflection="现在她不在了，但她的话我一直记着",
            legacy="她教给我的道理，我也传给了我的孩子"
        )
    elif t["theme"] == "重大事件":
        text = t["template"].format(
            year=random.choice(YEARS),
            event=random.choice(EVENTS),
            scene="那天街上人特别多，大家都在议论，广播里一直在播",
            action="我和家里人一起守在收音机前听消息，饭都顾不上吃",
            people_involved="单位组织我们集体观看，大家都激动得不得了",
            emotion1="心里既紧张又期待",
            immediate_impact="那天晚上激动得睡不着觉",
            emotion2="现在想起来，眼眶还是会湿",
            long_term_impact="从那以后，生活慢慢发生了变化，越来越好"
        )
    elif t["theme"] == "青春回忆":
        text = t["template"].format(
            activity=random.choice(ACTIVITIES),
            place_detail="就在离家不远的文化宫，那是我们唯一的娱乐场所",
            person="和一帮好朋友一起，大家都是十几岁的年轻人",
            sensory1="记得那时候的笑声和掌声",
            specific_memory="有一次我上台唱歌，紧张得忘词了，台下的人都在笑",
            sensory2="散场后我们会去吃路边摊，一碗馄饨都觉得是美味",
            nostalgia="现在再也没有那样的时光了",
            contrast="现在的年轻人可能理解不了那种简单的快乐"
        )
    elif t["theme"] == "迁徙经历":
        text = t["template"].format(
            year=random.choice(YEARS),
            origin="农村老家",
            destination="城里",
            reason="父亲工作调动，全家跟着搬过来",
            journey="坐了一整天的绿皮火车，又挤又闷",
            first_impression="城里的高楼让我眼花缭乱，马路宽得看不到头",
            difficulty="刚开始听不懂城里话，也没有朋友",
            adaptation="花了好几个月才适应，后来慢慢交了新朋友",
            memory="记得第一次去百货大楼，什么都觉得新鲜",
            feeling="现在想想，那是一次人生的转折点"
        )
    elif t["theme"] == "婚姻故事":
        text = t["template"].format(
            spouse="他",
            year=random.choice(YEARS),
            meeting_story="经人介绍认识的，第一次见面很害羞，话都不敢说",
            courtship="后来他经常来找我，帮我修自行车，送我自己做的东西",
            wedding="婚礼很简单，请了几个好朋友，买了些糖果瓜子",
            early_life="刚开始日子紧，两个人工资加起来才几十块",
            challenge="有了孩子后更困难，要照顾老人又要上班",
            life_together="一起走过了风风雨雨几十年，吵过架也拌过嘴",
            feeling_now="现在回想起来，还是很感激，他是个好人"
        )
    elif t["theme"] == "养育子女":
        text = t["template"].format(
            child="大儿子",
            trait="调皮但聪明，鬼点子多",
            memory1="记得有一次他逃学去玩，被老师找到家里",
            detail1="我气得要打他，他爸拦着说孩子还小",
            challenge="上学后成绩一直不错，但很让人操心",
            how_handled="我们尽量多陪他，跟他讲道理，不打不骂",
            pride="后来考上了大学，是我们家的骄傲",
            present="现在在外地工作，很少回来，但经常打电话",
            reflection="养儿方知父母恩，现在我也老了，能理解了"
        )
    else:
        # Fallback to simple template
        text = t["template"].format(
            age=random.randint(6, 12),
            place=random.choice(PLACES),
            sensory_detail=random.choice(SENSORY_DETAILS),
            emotion=random.choice(EMOTIONS),
            specific_event=random.choice(SPECIFIC_EVENTS),
            reflection=random.choice(REFLECTIONS)
        )
    
    return text, t["theme"]


def generate_boundary_sample():
    """生成边界案例样本"""
    template = random.choice(BOUNDARY_TEMPLATES)
    
    text = template.format(
        place=random.choice(PLACES),
        year=random.choice(YEARS),
        vague_event=random.choice(VAGUE_EVENTS),
        unclear_feeling="说不上来是什么感觉",
        workplace=random.choice(WORKPLACES),
        vague_routine=random.choice(VAGUE_EVENTS),
        pause="...",
        family_member=random.choice(FAMILY_MEMBERS),
        fuzzy_memory=random.choice(FRAGMENTS),
        uncertain="也许吧",
        mixed_events="工作、生活、家庭，各种事都有",
        confused="有时候想起来觉得乱",
        incomplete_story="后来因为一些原因就离开了",
        trailing_off="...",
        fragment=random.choice(FRAGMENTS),
        vague_connection="具体怎么回事说不清",
        vague_description="记不太清楚具体细节了",
        long_pause="...让我想想...",
        hesitation="就是...那个...",
        unclear_description="就是那些日常的事情"
    )
    
    return text, "边界案例"


def generate_stuffing_sample(stuffing_type=None):
    """生成堆砌样本"""
    if stuffing_type is None:
        stuffing_type = random.randint(0, len(STUFFING_TEMPLATES) - 1)
    
    text = STUFFING_TEMPLATES[stuffing_type]
    return text, f"堆砌-C{stuffing_type + 1}"


def main():
    samples = []
    
    # 生成 140 条正常叙述
    print("生成正常叙述样本 (140 条)...")
    for i in range(140):
        text, theme = generate_normal_sample(i % len(NORMAL_TEMPLATES))
        samples.append({
            "sample_id": f"N{i+1:03d}",
            "text": text,
            "type": "normal",
            "theme": theme,
            "expected_quality": "high",
            "word_count": len(text)
        })
    
    # 生成 40 条边界案例
    print("生成边界案例样本 (40 条)...")
    for i in range(40):
        text, sample_type = generate_boundary_sample()
        samples.append({
            "sample_id": f"B{i+1:03d}",
            "text": text,
            "type": "boundary",
            "theme": "混合",
            "expected_quality": "medium",
            "word_count": len(text)
        })
    
    # 生成 20 条堆砌样本
    print("生成堆砌样本 (20 条)...")
    for i in range(20):
        text, sample_type = generate_stuffing_sample(i % len(STUFFING_TEMPLATES))
        samples.append({
            "sample_id": f"S{i+1:03d}",
            "text": text,
            "type": "stuffing",
            "theme": sample_type,
            "expected_quality": "low",
            "word_count": len(text)
        })
    
    # 写入 CSV
    output_path = "/Users/moondy/.openclaw/workspace-hulk/data/samples/exp-001-samples.csv"
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["sample_id", "text", "type", "theme", "expected_quality", "word_count"])
        writer.writeheader()
        writer.writerows(samples)
    
    print(f"\n✅ 样本生成完成：{output_path}")
    print(f"   总样本数：{len(samples)}")
    print(f"   - 正常叙述：140 条")
    print(f"   - 边界案例：40 条")
    print(f"   - 堆砌样本：20 条")
    
    # 统计字数分布
    normal_avg = sum(s["word_count"] for s in samples if s["type"] == "normal") / 140
    boundary_avg = sum(s["word_count"] for s in samples if s["type"] == "boundary") / 40
    stuffing_avg = sum(s["word_count"] for s in samples if s["type"] == "stuffing") / 20
    
    print(f"\n字数统计:")
    print(f"   - 正常叙述平均：{normal_avg:.0f} 字")
    print(f"   - 边界案例平均：{boundary_avg:.0f} 字")
    print(f"   - 堆砌样本平均：{stuffing_avg:.0f} 字")


if __name__ == "__main__":
    main()
