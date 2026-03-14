#!/usr/bin/env python3
"""
ASR Selection Test Framework for CittaVerse

Purpose: Evaluate ASR APIs for elderly speech transcription accuracy
Target: MCI/dementia patients with acoustic feature anomalies

Tested ASR Services:
1. Azure Speech (medical customization)
2. iFlytek 讯飞听见 (Chinese elderly optimization)
3. Whisper (baseline, known issues per CHI 2026)

Evaluation Metrics:
- WER (Word Error Rate): Primary metric
- CER (Character Error Rate): For Chinese
- Latency: Time-to-transcription
- Cost: Per minute pricing
- Dialect Support: Mandarin, Cantonese, regional accents

CHI 2026 Reference:
- Whisper shows significant accuracy drop for dementia patients
- Root cause: Acoustic feature anomalies (speech rate, pauses, clarity)
- Implication: Need specialized ASR for target population

Author: Hulk 🟢
Created: 2026-03-14
Status: Framework ready, awaiting API keys and test samples
"""

import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime

# ============================================================================
# Configuration
# ============================================================================

@dataclass
class ASRConfig:
    name: str
    api_key_env: str
    base_url: str
    supported_languages: List[str]
    pricing_per_minute: float
    medical_customization: bool
    elderly_optimization: bool

# ASR Service Configurations
ASR_SERVICES = {
    "azure_speech": ASRConfig(
        name="Azure Speech",
        api_key_env="AZURE_SPEECH_KEY",
        base_url="https://<region>.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1",
        supported_languages=["zh-CN", "en-US", "yue-CN"],
        pricing_per_minute=0.01,  # $0.01/min for standard
        medical_customization=True,
        elderly_optimization=False  # But has medical customization
    ),
    "iflytek": ASRConfig(
        name="iFlytek 讯飞听见",
        api_key_env="IFLYTEK_API_KEY",
        base_url="https://api-open.xfyun.cn/v2/iat",
        supported_languages=["zh-CN", "zh-HK", "en-US"],
        pricing_per_minute=0.008,  # ~¥0.05/min
        medical_customization=False,
        elderly_optimization=True  # Optimized for Chinese elderly
    ),
    "whisper": ASRConfig(
        name="Whisper (OpenAI)",
        api_key_env="OPENAI_API_KEY",
        base_url="https://api.openai.com/v1/audio/transcriptions",
        supported_languages=["multilingual"],
        pricing_per_minute=0.006,  # $0.006/min (whisper-1)
        medical_customization=False,
        elderly_optimization=False
    )
}

# ============================================================================
# Test Data Structure
# ============================================================================

@dataclass
class TestSample:
    id: str
    audio_path: str
    duration_seconds: float
    speaker_profile: str  # "healthy_elderly", "mci_mild", "dementia_moderate"
    dialect: str
    ground_truth_text: str  # Manual transcription for WER calculation
    difficulty_level: int  # 1-5 (5=most difficult)

@dataclass
class ASRResult:
    service_name: str
    sample_id: str
    transcribed_text: str
    wer: float  # Word Error Rate
    cer: float  # Character Error Rate (for Chinese)
    latency_ms: float
    cost_usd: float
    error_message: Optional[str]
    timestamp: str

@dataclass
class EvaluationReport:
    test_run_id: str
    start_time: str
    end_time: str
    total_samples: int
    results: List[ASRResult]
    summary: Dict[str, Dict[str, float]]

# ============================================================================
# WER/CER Calculation
# ============================================================================

def calculate_wer(reference: str, hypothesis: str) -> float:
    """
    Calculate Word Error Rate using Levenshtein distance.
    WER = (S + D + I) / N
    where S=substitutions, D=deletions, I=insertions, N=total words in reference
    """
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    
    # Dynamic programming for edit distance
    m, n = len(ref_words), len(hyp_words)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref_words[i-1] == hyp_words[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    
    return dp[m][n] / max(m, 1)

def calculate_cer(reference: str, hypothesis: str) -> float:
    """
    Calculate Character Error Rate for Chinese text.
    Same formula as WER but at character level.
    """
    ref_chars = list(reference.replace(" ", ""))
    hyp_chars = list(hypothesis.replace(" ", ""))
    
    m, n = len(ref_chars), len(hyp_chars)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref_chars[i-1] == hyp_chars[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    
    return dp[m][n] / max(m, 1)

# ============================================================================
# ASR Service Clients (Stubs - to be implemented with actual API calls)
# ============================================================================

class ASRClient:
    def __init__(self, config: ASRConfig):
        self.config = config
        self.api_key = None  # Will be loaded from environment
    
    def transcribe(self, audio_path: str) -> tuple[str, float]:
        """
        Transcribe audio file and return (text, latency_ms).
        To be implemented for each service.
        """
        raise NotImplementedError

class AzureSpeechClient(ASRClient):
    def transcribe(self, audio_path: str) -> tuple[str, float]:
        # TODO: Implement Azure Speech API call
        # Reference: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-speech-to-text
        return "TODO: Azure transcription", 0.0

class IFlytekClient(ASRClient):
    def transcribe(self, audio_path: str) -> tuple[str, float]:
        # TODO: Implement iFlytek API call
        # Reference: https://www.xfyun.cn/doc/asr/voicedictation/API.html
        return "TODO: iFlytek transcription", 0.0

class WhisperClient(ASRClient):
    def transcribe(self, audio_path: str) -> tuple[str, float]:
        # TODO: Implement Whisper API call via OpenAI
        # Reference: https://platform.openai.com/docs/guides/speech-to-text
        return "TODO: Whisper transcription", 0.0

# ============================================================================
# Test Runner
# ============================================================================

class ASREvaluationTest:
    def __init__(self, test_samples: List[TestSample], output_dir: str = "./asr_test_results"):
        self.test_samples = test_samples
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[ASRResult] = []
    
    def run_test(self, service_name: str) -> List[ASRResult]:
        """Run evaluation for a single ASR service."""
        config = ASR_SERVICES.get(service_name)
        if not config:
            raise ValueError(f"Unknown service: {service_name}")
        
        client = self._create_client(service_name, config)
        results = []
        
        for sample in self.test_samples:
            start_time = time.time()
            try:
                transcribed_text, _ = client.transcribe(sample.audio_path)
                latency_ms = (time.time() - start_time) * 1000
                
                wer = calculate_wer(sample.ground_truth_text, transcribed_text)
                cer = calculate_cer(sample.ground_truth_text, transcribed_text)
                cost = (sample.duration_seconds / 60) * config.pricing_per_minute
                
                result = ASRResult(
                    service_name=service_name,
                    sample_id=sample.id,
                    transcribed_text=transcribed_text,
                    wer=wer,
                    cer=cer,
                    latency_ms=latency_ms,
                    cost_usd=cost,
                    error_message=None,
                    timestamp=datetime.utcnow().isoformat()
                )
            except Exception as e:
                result = ASRResult(
                    service_name=service_name,
                    sample_id=sample.id,
                    transcribed_text="",
                    wer=1.0,  # Max error
                    cer=1.0,
                    latency_ms=0.0,
                    cost_usd=0.0,
                    error_message=str(e),
                    timestamp=datetime.utcnow().isoformat()
                )
            
            results.append(result)
            print(f"  [{sample.id}] WER: {wer:.3f}, CER: {cer:.3f}, Latency: {latency_ms:.1f}ms")
        
        return results
    
    def _create_client(self, service_name: str, config: ASRConfig) -> ASRClient:
        client_map = {
            "azure_speech": AzureSpeechClient,
            "iflytek": IFlytekClient,
            "whisper": WhisperClient
        }
        return client_map[service_name](config)
    
    def generate_report(self) -> EvaluationReport:
        """Generate evaluation report with summary statistics."""
        summary = {}
        for service_name in ASR_SERVICES.keys():
            service_results = [r for r in self.results if r.service_name == service_name]
            if service_results:
                summary[service_name] = {
                    "avg_wer": sum(r.wer for r in service_results) / len(service_results),
                    "avg_cer": sum(r.cer for r in service_results) / len(service_results),
                    "avg_latency_ms": sum(r.latency_ms for r in service_results) / len(service_results),
                    "avg_cost_per_sample": sum(r.cost_usd for r in service_results) / len(service_results),
                    "success_rate": sum(1 for r in service_results if r.error_message is None) / len(service_results)
                }
        
        report = EvaluationReport(
            test_run_id=datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
            start_time=self.results[0].timestamp if self.results else "",
            end_time=self.results[-1].timestamp if self.results else "",
            total_samples=len(self.test_samples),
            results=self.results,
            summary=summary
        )
        
        # Save report
        report_path = self.output_dir / f"asr_evaluation_{report.test_run_id}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(asdict(report), f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Report saved: {report_path}")
        return report

# ============================================================================
# Main Execution
# ============================================================================

def create_test_samples() -> List[TestSample]:
    """
    Create test samples from elderly speech datasets.
    TODO: Replace with actual audio files and ground truth.
    """
    # Placeholder samples - to be replaced with real data
    return [
        TestSample(
            id="elderly_001",
            audio_path="./test_samples/elderly_001.wav",
            duration_seconds=30.0,
            speaker_profile="healthy_elderly",
            dialect="zh-CN",
            ground_truth_text="我今天早上去了公园散步，天气很好。",
            difficulty_level=2
        ),
        TestSample(
            id="mci_001",
            audio_path="./test_samples/mci_001.wav",
            duration_seconds=45.0,
            speaker_profile="mci_mild",
            dialect="zh-CN",
            ground_truth_text="那个...我想想...昨天我女儿来看我了，她带了...带了...",
            difficulty_level=4
        ),
        TestSample(
            id="dementia_001",
            audio_path="./test_samples/dementia_001.wav",
            duration_seconds=60.0,
            speaker_profile="dementia_moderate",
            dialect="zh-CN",
            ground_truth_text="嗯...这个...在哪里...我记不清了...",
            difficulty_level=5
        ),
    ]

def main():
    print("=" * 70)
    print("ASR Selection Test Framework for CittaVerse")
    print("=" * 70)
    print(f"\n📋 Test Configuration:")
    print(f"  Services to test: {list(ASR_SERVICES.keys())}")
    print(f"  Output directory: ./asr_test_results")
    print(f"\n📊 Evaluation Metrics:")
    print(f"  - WER (Word Error Rate): Primary metric")
    print(f"  - CER (Character Error Rate): For Chinese")
    print(f"  - Latency: Time-to-transcription (ms)")
    print(f"  - Cost: USD per minute")
    print(f"\n⚠️  CHI 2026 Reference:")
    print(f"  - Whisper shows significant accuracy drop for dementia patients")
    print(f"  - Root cause: Acoustic feature anomalies")
    print(f"  - Recommendation: Test Azure Speech + iFlytek for elderly optimization")
    print("\n" + "=" * 70)
    
    # Create test samples
    test_samples = create_test_samples()
    print(f"\n📁 Test Samples: {len(test_samples)}")
    for sample in test_samples:
        print(f"  - {sample.id}: {sample.speaker_profile}, {sample.dialect}, Level {sample.difficulty_level}")
    
    # Initialize test runner
    test_runner = ASREvaluationTest(test_samples)
    
    # Run tests for each service
    print("\n🚀 Running ASR Evaluation Tests...")
    for service_name in ASR_SERVICES.keys():
        print(f"\n  Testing {service_name}...")
        try:
            results = test_runner.run_test(service_name)
            test_runner.results.extend(results)
        except Exception as e:
            print(f"  ❌ Error testing {service_name}: {e}")
    
    # Generate report
    if test_runner.results:
        print("\n📈 Generating Evaluation Report...")
        report = test_runner.generate_report()
        
        # Print summary
        print("\n" + "=" * 70)
        print("EVALUATION SUMMARY")
        print("=" * 70)
        for service_name, metrics in report.summary.items():
            print(f"\n{ASR_SERVICES[service_name].name}:")
            print(f"  Avg WER: {metrics['avg_wer']:.3f} (lower is better)")
            print(f"  Avg CER: {metrics['avg_cer']:.3f} (lower is better)")
            print(f"  Avg Latency: {metrics['avg_latency_ms']:.1f}ms")
            print(f"  Success Rate: {metrics['success_rate']:.1%}")
        
        print("\n" + "=" * 70)
        print("✅ ASR Evaluation Complete")
        print("=" * 70)
    else:
        print("\n⚠️  No results generated. Check API key configuration and test samples.")

if __name__ == "__main__":
    main()
