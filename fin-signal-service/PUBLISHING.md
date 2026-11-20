# 發布學習網站到 GitHub Pages

## 首次設定

1. 開啟 GitHub repository 的 Settings → Pages。
2. 將 Build and deployment → Source 設為 GitHub Actions。
3. 將課程檔案與 `.github/workflows/deploy-learning-pages.yml` 提交、推送到 `main`。
4. 在 repository 的 Actions 頁面開啟 `Publish learning pages`，等待部署成功。
5. 從成功執行紀錄的 deployment 連結開啟網站；也可在 Settings → Pages 查看網址。

依目前 repository 名稱，預期網址為：

https://qn5566.github.io/ai_studio/

實際網址以 GitHub 顯示的結果為準。首次部署成功前，這個網址可能顯示 404。

## 發布內容

工作流程只複製以下教材檔案作為網站內容：

| 專案內的檔案 | 網站上的位置 |
| --- | --- |
| `fin-signal-service/LEARNING_PROGRESS.html` | `index.html`，開啟網站即可看到課表 |
| `fin-signal-service/LEARNING_PROGRESS.md` | `LEARNING_PROGRESS.md`，供頁面上的原始紀錄連結使用 |
| `fin-signal-service/book/chapter-01.html` | `book/chapter-01.html`，第一章互動教材 |

不需要安裝 Python、執行 FastAPI 或購買伺服器。GitHub Pages 提供靜態檔案託管。

## 更新課程

修改課表 HTML、Markdown 或 `book/` 裡的教材並推送到 `main`，會再次觸發部署。課表 HTML 內含一份供匯出的 Markdown 內容，更新筆記時也應同步該內容。

若要手動重發目前版本，可到 Actions → Publish learning pages → Run workflow，選擇 `main` 執行。

## 手機複習

用手機開啟網站後，可加入書籤，或透過瀏覽器功能加入主畫面。

勾選進度保存在各自瀏覽器，不會自動同步到其他裝置或 GitHub。切換裝置可使用頁面上的「下載進度備份」與「匯入備份」。本機檔案與正式網址的瀏覽器儲存空間也各自獨立。

第一章教材有「下載完整 HTML」功能，儲存到裝置後可離線閱讀，互動功能需要使用支援 JavaScript 的瀏覽器開啟。部分手機檔案預覽器只顯示內容而不執行 JavaScript。

網站網址目前未實作離線快取；沒有網路時不保證可以重新開啟網站。教材頁的閱讀標記、答案與書籤，使用獨立於原課表的儲存紀錄，也有自己的備份與匯入功能。
