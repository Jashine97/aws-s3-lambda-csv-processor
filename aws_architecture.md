# AWS Architecture

```
Upload CSV
    ↓
┌──────────────┐
│  S3 Raw Data │
└──────────────┘
        ↓ (event trigger)
┌────────────────────┐
│  Lambda Processor  │
└────────────────────┘
        ↓
┌──────────────────────────┐
│  S3 Processed Summaries  │
└──────────────────────────┘
```
