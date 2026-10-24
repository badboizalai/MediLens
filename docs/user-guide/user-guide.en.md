# MediLens user guide (draft)

> Draft for review by the Clinical Safety Officer and the regulatory owner. Not yet published to users. Screenshots are placeholders. Features marked **Coming soon** are built in the backend or as components but cannot be reached from the app yet.

MediLens helps you understand your own medical records. Use it alongside your doctor's advice.

## What MediLens does not do
- It does not tell you what condition you have. MediLens works alongside your doctor, not instead of them.
- It does not suggest medicines, amounts of medicine, or whether to stop or change a medicine.
- It does not predict how an illness will progress or how long anything will last.
- Colours on the body map only show what is written in your record. They are an illustration.
- **In an emergency (for example severe chest pain, trouble breathing, heavy bleeding), call 115 or go to the nearest emergency department. Do not use this app.**

If you ask MediLens about medicine amounts or outlook, it declines and points you to your care team. If you describe emergency signs, it shows the 115 message first.

## 1. Sign in
Open MediLens and choose **Continue to sign in**. After signing in you see **Your records** with an **Add a record** link.
*[Screenshot placeholder: sign-in page with the single "Continue to sign in" button.]*

## 2. Add a record
1. Choose **Add a record** (the page is titled "Add a medical record").
2. Choose **Take photo** or **Choose file**, or drop a file on the page. Accepted: JPG, PNG, HEIC or PDF, up to 20 MB per file and 30 pages per document.
3. Check the list of **Selected pages**. You can move a page up or down, or remove it.
4. Choose **Upload**. If the connection drops, choose **Retry**.

If a file is the wrong type, too large, empty, or has too many pages, you see a message saying which file and why. Uploading the same file twice does not create a second record.
*[Screenshot placeholder: upload page with three selected pages and the tips panel.]*

## 3. Take a clear photo (and fix a blurry one)
See the [capture guide](capture-guide.en.md). In short: bright even light, page flat, phone straight above, all four corners in view, no flash on glossy paper, cover other people's names.

While your record is read you see the steps *Waiting to start*, *Reading your record* and *Finding the details*. It takes about 2 minutes and you can leave the page.

If a photo cannot be read, the screen says **Let's try another photo** with the reason:
- *Blurry*: retake in good light, holding the phone parallel to the page.
- *Too dark*: retake in a brighter place, without flash on glossy paper.
- *Not a document*: put the whole page in view.

Choose **Take a new photo**. This is normal and does not mean you did something wrong. If the file cannot be accepted at all, you see **We couldn't accept this file** and **Upload again**.
*[Screenshot placeholder: "Let's try another photo" screen with the blurry reason.]*

## 4. Check and confirm the fields
When the draft is ready, choose **Check your record**.
1. Each field shows where it came from: **AI extracted**, **You edited** or **Confirmed**.
2. Fields marked **Needs check** are ones MediLens is not sure about. You must check these.
3. Choose **Show on page** to see the original page with the spot highlighted. If the preview is not available, the screen says so.
4. Edit the value and choose **Save change**, or choose **Confirm this value**.
5. The counter shows how many items are left. When none are left, choose **Confirm document**. If something still needs checking, the screen lists it and does not confirm.

Only confirmed information appears on the body view and can be shared. Please check every field, because AI can misread.
*[Screenshot placeholder: review screen with one yellow "Needs check" field and the page preview.]*

## 5. Read the body map
Open the profile body page. You see the front and back of the body and a list of **Regions with findings**.
- Each region is coloured and also labelled in words: *Monitor*, *Mild*, *Moderate*, *Severe*, *Metastasis / spread*, *Reference*. Colour is never the only signal.
- Spread (metastasis) appears only when your record states it.
- On a device that supports it you can use the **3D view**: drag to rotate, scroll to zoom, click a coloured region, press Escape to reset. Choose **Switch to 2D map** at any time. On slow devices, or with data saving on, MediLens shows the 2D map and tells you why.
- For now the 3D models are simple stand-in shapes, not detailed anatomy.

*[Screenshot placeholder: 2D body map with the region list. Second placeholder: 3D view with a selected region.]*

**Teeth chart: coming soon.** The tooth chart (FDI numbering) exists as a component but has no page in the app yet.

## 6. Compare two visits
Open the timeline page (**Compare two visits**). Pick a **First visit** and a **Second visit**. You see the body view for each, a list of what is **Listed only in the first visit**, **Listed only in the second visit** or **Listed in both visits**, and measurements side by side. With only one confirmed visit there is nothing to compare yet.

The list only shows what each record mentions. It does not say whether anything is better or worse. Ask your doctor what it means.
*[Screenshot placeholder: timeline with two visits and the differences list.]*

## 7. Describe a symptom yourself
**Coming soon.** The backend can store things you describe in your own words. They will always be labelled "you described", with no medical code and no severity colour. There is no screen for this in the app yet. If you describe emergency signs, the 115 message comes first.

## 8. Ask for an explanation
**Coming soon.** Plain-language explanations with sources are built in the backend, but there is no screen for them yet. The articles behind them are drafts waiting for clinical review.

## 9. Share with a clinician, and stop sharing
Open **Share with a clinician** for the profile.
1. Enter the recipient's user ID. They must have a MediLens account and give you their ID.
2. Choose how long access lasts (from 1 hour up to 7 days). It ends automatically.
3. Choose **Create share**. What is shared: confirmed findings, view only.
4. Under **Your shares** you see each share as *Active*, *Expired* or *Revoked*, with the time left.
5. To stop sooner, choose **Revoke**, then **Yes, revoke**. Access ends right away.

The recipient sees a "view only" banner, cannot edit or download, and sees a watermark with their ID, the share and the end time. After the share ends they see **Access has ended**.
*[Screenshot placeholder: sharing page with one active share. Second placeholder: the clinician view with watermark.]*

## 10. Download or delete your data
**Not available in the app yet.** There is no download or delete button today. Until it is built, ask the MediLens team through the support channel you were given, and we will handle your request as the privacy notice describes.

## 11. Privacy
- Your records are health data. Only you can see them, unless you share.
- Photograph in a private place and cover other people's details.
- Upload only records you are allowed to share.
- Shares are view-only, time-limited and can be revoked.
- Personal details are removed before text is sent to AI services.

## Quick help
| Problem | What to do |
| --- | --- |
| "Let's try another photo" | Follow the tip shown and retake |
| Upload stops | Choose **Retry** |
| Cannot confirm the document | Check the items listed as still needing your check |
| Shared record says access ended | Ask the owner for a new share |
