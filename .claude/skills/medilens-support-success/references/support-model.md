# Support model

## Tiers
| Tier | Who | Handles |
| --- | --- | --- |
| L1 | Support (macros, KB) | how-to, account, upload tips, known issues, routing |
| L2 | Product/engineering on rotation (BE/FE/AI) | reproduce, logs via trace id, workaround |
| L3 | Owner skill | code/infra/model fix through normal PR flow |

## SLAs (business hours, solo-project realistic)
| Severity | First response | Update cadence | Target resolution |
| --- | --- | --- | --- |
| S1 — service unusable / safety class A / data exposure | 1 h (alert-driven) | every 2 h | workaround same day |
| S2 — major feature broken, no workaround | 4 h | daily | 2 working days |
| S3 — feature impaired, workaround exists | 1 working day | on change | next release |
| S4 — question, cosmetic, idea | 2 working days | — | backlog |

## Channels
In-app help form (pre-fills app version, trace id, locale; never auto-attaches records), email support address, status page for incidents. No phone support in v1.

## Hours
Published support hours (e.g., weekdays 9:00–17:00 ICT); automatic acknowledgement outside hours with emergency guidance (115) and self-help links.
