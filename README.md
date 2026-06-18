# Intelligent Document Processing (IDP) Agent

Bu proje, çeşitli belge formatlarından (PDF, taranmış belgeler, faturalar, sözleşmeler vb.) yüksek doğrulukla yapılandırılmış veri ayıklayan üretim seviyesinde bir **Document AI / IDP** aracıdır.

Proje, gücünü **Google Gemini API** (`gemini-2.5-flash` modeli) ve **Pydantic** yapılandırılmış çıktı doğrulamalarından alır.

## Özellikler

- **Çoklu Format Desteği**: PDF, PNG, JPG ve JPEG formatlarındaki belgeleri doğrudan işleyebilir.
- **Yapılandırılmış JSON Çıktısı**: Çıktılar önceden tanımlanmış Pydantic veri şemasına göre birebir doğrulanarak üretilir.
- **Otomatik Dil Tespiti**: Belgelerin orijinal dillerini otomatik tespit eder.
- **Güven Analizi**: Sınıflandırma ve ayıklama işlemleri için güven puanı (`confidence_score`) üretir.
- **Hata Yönetimi**: Boş, bozuk veya okunamayan belgeler için standart `UNREADABLE_DOCUMENT` hata şemasını döner.

---

## Kurulum

### 1. Gereksinimler

Sisteminizde Python 3.10 veya üzeri yüklü olmalıdır.

### 2. Bağımlılıkları Yükleme

Terminal veya PowerShell üzerinde aşağıdaki komut ile gerekli kütüphaneleri yükleyin:

```bash
pip install -r requirements.txt
```

---

## Kullanım

### 1. API Anahtarını Tanımlama

Gemini API anahtarınızı çevre değişkeni (environment variable) olarak ekleyin:

**PowerShell (Windows):**

```powershell
$env:GEMINI_API_KEY="kendi-api-anahtariniz"
```

**Bash (Linux/macOS):**

```bash
export GEMINI_API_KEY="kendi-api-anahtariniz"
```

### 2. Uygulamayı Çalıştırma

Analiz etmek istediğiniz belgenin yolunu argüman olarak vererek betiği çalıştırın:

```bash
python idp_agent.py test_inputs/ornek_sozlesme.txt
```

---

## Beklenen Çıktı Şeması

Başarılı analizlerde aşağıdaki standart JSON yapısı elde edilir:

```json
{
  "document_analysis": {
    "metadata": {
      "document_type": "String",
      "language": "String",
      "page_count": "Integer or null",
      "classification_confidence": 0.0
    },
    "extracted_data": {
      "identifiers": {
        "document_number": "String or null",
        "reference_numbers": ["String"]
      },
      "dates": {
        "issue_date": "String or null",
        "expiry_date": "String or null",
        "other_relevant_dates": {}
      },
      "parties": {
        "issuer_or_sender": "String or null",
        "recipient_or_buyer": "String or null",
        "signatories": ["String"]
      },
      "financials": {
        "currency": "String or null",
        "subtotal": "Float or null",
        "tax_amount": "Float or null",
        "total_amount": "Float or null"
      }
    },
    "tables_and_lists": [
      {
        "table_name": "String",
        "headers": ["String"],
        "rows": [
          {
            "item_index": 1,
            "details": {}
          }
        ]
      }
    ],
    "validation_and_flags": {
      "has_signature": "Boolean",
      "has_stamp_or_seal": "Boolean",
      "potential_anomalies": ["String"],
      "extraction_confidence_score": 0.0
    },
    "semantic_summary": "String"
  }
}
```

---

## Testleri Çalıştırma

Projede yer alan hata durumları ve parametre kontrolleri için unit testleri koşturabilirsiniz:

```bash
python -m pytest -v
```

---

# Intelligent Document Processing (IDP) Agent (English)

This project is a production-grade **Document AI / IDP** tool that extracts structured information from various document formats (PDF, scanned images, invoices, contracts, etc.) with maximum precision.

The project is powered by the **Google Gemini API** (`gemini-2.5-flash` model) and **Pydantic** structured output validation.

## Features

- **Multi-Format Support**: Direct processing of PDF, PNG, JPG, and JPEG documents.
- **Structured JSON Output**: Outputs are strictly validated against a predefined Pydantic schema.
- **Language Auto-Detection**: Automatically detects the original language of the document.
- **Confidence Scoring**: Provides confidence scores for classification and extraction.
- **Error Handling**: Returns a standard `UNREADABLE_DOCUMENT` error schema for blank, corrupted, or unreadable files.

---

## Installation

### 1. Requirements

Python 3.10 or higher must be installed on your system.

### 2. Install Dependencies

Install the required packages using pip:

```bash
pip install -r requirements.txt
```

---

## Usage

### 1. Configure API Key

Set your Gemini API key as an environment variable:

**PowerShell (Windows):**

```powershell
$env:GEMINI_API_KEY="your-api-key"
```

**Bash (Linux/macOS):**

```bash
export GEMINI_API_KEY="your-api-key"
```

### 2. Run the Application

Execute the script by passing the path of the document you want to analyze as an argument:

```bash
python idp_agent.py test_inputs/ornek_sozlesme.txt
```

---

## Expected Output Schema

Successful analyses return the following standard JSON structure:

```json
{
  "document_analysis": {
    "metadata": {
      "document_type": "String",
      "language": "String",
      "page_count": "Integer or null",
      "classification_confidence": 0.0
    },
    "extracted_data": {
      "identifiers": {
        "document_number": "String or null",
        "reference_numbers": ["String"]
      },
      "dates": {
        "issue_date": "String or null",
        "expiry_date": "String or null",
        "other_relevant_dates": {}
      },
      "parties": {
        "issuer_or_sender": "String or null",
        "recipient_or_buyer": "String or null",
        "signatories": ["String"]
      },
      "financials": {
        "currency": "String or null",
        "subtotal": "Float or null",
        "tax_amount": "Float or null",
        "total_amount": "Float or null"
      }
    },
    "tables_and_lists": [
      {
        "table_name": "String",
        "headers": ["String"],
        "rows": [
          {
            "item_index": 1,
            "details": {}
          }
        ]
      }
    ],
    "validation_and_flags": {
      "has_signature": "Boolean",
      "has_stamp_or_seal": "Boolean",
      "potential_anomalies": ["String"],
      "extraction_confidence_score": 0.0
    },
    "semantic_summary": "String"
  }
}
```

---

## Running Tests

Run the unit tests to check error scenarios and parameter validation:

```bash
python -m pytest -v
```
