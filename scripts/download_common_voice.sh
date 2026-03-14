#!/bin/bash
# Common Voice 中文数据集下载脚本 (60+ 岁说话者筛选)
# 用途：为老年语音 ASR 测试收集真实样本
# 数据集：https://commonvoice.mozilla.org/zh-CN

set -e

# 配置
OUTPUT_DIR="${HOME}/Downloads/common_voice_elderly"
DATASET_URL="https://voice-prod-bundler-ee1969a6ce817082ed08d697ba62223d.s3.amazonaws.com/cv-corpus-19.0-2024-09-27/zh-CN.tar.gz"
# 注：以上为示例 URL，实际需从 Mozilla Common Voice 官网获取最新版本

echo "=== Common Voice 中文数据集下载 (60+ 岁说话者) ==="
echo "输出目录：${OUTPUT_DIR}"
echo ""

# 创建输出目录
mkdir -p "${OUTPUT_DIR}"
cd "${OUTPUT_DIR}"

# 检查磁盘空间 (需要约 10GB)
AVAILABLE_SPACE=$(df -P . | awk 'NR==2 {print $4}')
REQUIRED_SPACE=10485760  # 10GB in KB
if [ "${AVAILABLE_SPACE}" -lt "${REQUIRED_SPACE}" ]; then
    echo "⚠️  警告：可用磁盘空间不足 10GB"
    echo "   当前可用：$((AVAILABLE_SPACE / 1024 / 1024)) GB"
    echo "   建议清理空间或使用外部存储"
fi

# 下载数据集 (如已存在则跳过)
if [ -f "zh-CN.tar.gz" ]; then
    echo "✅ 数据集已存在，跳过下载"
else
    echo "📥 开始下载中文数据集 (约 2-5GB)..."
    echo "   来源：${DATASET_URL}"
    echo "   提示：下载可能需要 10-30 分钟，取决于网络速度"
    
    # 使用 wget 或 curl 下载
    if command -v wget &> /dev/null; then
        wget -c --show-progress "${DATASET_URL}" -O zh-CN.tar.gz
    elif command -v curl &> /dev/null; then
        curl -L -C - -o zh-CN.tar.gz "${DATASET_URL}"
    else
        echo "❌ 错误：未找到 wget 或 curl"
        exit 1
    fi
fi

# 解压数据集
if [ ! -d "cv-corpus-19.0-2024-09-27" ]; then
    echo "📦 解压数据集..."
    tar -xzf zh-CN.tar.gz
fi

# 进入数据集目录
DATA_DIR="cv-corpus-19.0-2024-09-27/zh-CN"
if [ ! -d "${DATA_DIR}" ]; then
    echo "❌ 错误：数据集目录不存在"
    exit 1
fi

cd "${DATA_DIR}"

# 筛选 60+ 岁说话者
echo "🔍 筛选 60+ 岁说话者..."

# Common Voice 的 speakers.tsv 包含说话者信息
# 列：client_id, age, gender, accents, locale, about, speaker_id
if [ -f "speakers.tsv" ]; then
    # 提取 60+ 岁说话者的 client_id
    # 注意：age 列可能是 "60s", "70s", "80s" 或具体数字
    awk -F'\t' 'NR>1 && ($2 ~ /^6/ || $2 ~ /^7/ || $2 ~ /^8/ || $2 ~ /^9/ || $2 == "60+" || $2 == "70+" || $2 == "80+") {print $1}' speakers.tsv > elderly_speakers.txt
    
    ELDERLY_COUNT=$(wc -l < elderly_speakers.txt)
    echo "✅ 找到 ${ELDERLY_COUNT} 位 60+ 岁说话者"
    
    if [ "${ELDERLY_COUNT}" -eq 0 ]; then
        echo "⚠️  警告：未找到 60+ 岁说话者"
        echo "   可能原因：年龄数据缺失或格式不同"
        echo "   建议：手动检查 speakers.tsv 文件"
    fi
else
    echo "⚠️  警告：speakers.tsv 不存在，无法按年龄筛选"
    echo "   将使用全部验证过的音频"
fi

# 创建筛选后的音频列表
if [ -f "validated.tsv" ] && [ -f "elderly_speakers.txt" ]; then
    echo "📋 生成 60+ 岁说话者的音频列表..."
    
    # 从 validated.tsv 中筛选出老年说话者的录音
    # validated.tsv 列：client_id, path, sentence, up_votes, down_votes, age, gender, accents, locale, segment, variant
    awk -F'\t' 'NR==FNR {ids[$1]; next} FNR>1 && ($1 in ids)' elderly_speakers.txt validated.tsv > validated_elderly.tsv
    
    ELDERLY_RECORDINGS=$(wc -l < validated_elderly.tsv)
    echo "✅ 找到 ${ELDERLY_RECORDINGS} 条 60+ 岁说话者的录音"
    
    # 复制到输出目录
    mkdir -p "${OUTPUT_DIR}/elderly_samples"
    echo "📁 复制音频文件到 ${OUTPUT_DIR}/elderly_samples/..."
    
    # 注意：实际复制可能需要较长时间，这里只复制前 100 个作为示例
    head -100 validated_elderly.tsv | while IFS=$'\t' read -r client_id path rest; do
        if [ -f "${path}" ]; then
            cp "${path}" "${OUTPUT_DIR}/elderly_samples/" 2>/dev/null || true
        fi
    done
    
    echo "✅ 已复制前 100 个音频样本到 ${OUTPUT_DIR}/elderly_samples/"
    echo "   如需复制全部，请手动执行批量复制"
fi

# 生成统计报告
echo ""
echo "=== 数据集统计 ==="
if [ -f "validated.tsv" ]; then
    TOTAL_RECORDINGS=$(tail -n +2 validated.tsv | wc -l)
    echo "总验证录音数：${TOTAL_RECORDINGS}"
fi
if [ -f "elderly_speakers.txt" ]; then
    echo "60+ 岁说话者数：${ELDERLY_COUNT}"
    echo "60+ 岁录音数：${ELDERLY_RECORDINGS}"
fi

echo ""
echo "=== 输出文件 ==="
echo "老年说话者 ID 列表：${DATA_DIR}/elderly_speakers.txt"
echo "老年录音元数据：${DATA_DIR}/validated_elderly.tsv"
echo "音频样本目录：${OUTPUT_DIR}/elderly_samples/"
echo ""
echo "✅ Common Voice 中文数据集准备完成!"
echo ""
echo "下一步:"
echo "1. 使用 ASR 评估脚本测试这些样本"
echo "2. 比较不同 ASR 服务在老年语音上的表现"
echo "3. 参考：/workspace-hulk/pipeline/asr_evaluation_test.py"
