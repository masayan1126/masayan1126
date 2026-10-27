# お問い合わせの送信API

`studio.msyn.me/api/contact` で受けた内容を、Cloudflare Email Routingで送ります。受信先の `TO` と `TURNSTILE_SECRET_KEY` はWorkerのシークレットに保存します。

送信前に、正規サイトのOrigin、フォーム形式と64 KiB以内の実データ、入力項目を確認します。TurnstileのSiteverifyで成功・ホスト名 `studio.msyn.me`・action `contact` が一致した場合だけメールを送ります。認証や設定の障害時には送信しません。

同じIPからのPOSTに、Cloudflare拠点ごとに1分5回の制限を設定しています。カウンターの同期に短い遅延があり、厳密な上限ではありません。隠し入力欄が埋まったリクエストには成功を返しますが、メールは送りません。本文・IP・認証トークン・シークレットはログに記録しません。

公開サイトのsitekeyは `canvas/v3/contact-security.json`、秘密鍵はWorker側で管理します。ローカルHTMLでは公式のテスト用sitekeyに置き換え、送信は既存のプレビュー処理で止めます。公開用ビルドはテスト用sitekeyを受け付けません。`pages.dev/contact/` はJavaScriptで正規サイトへ移動します。

`npm test` でAPIと画面の検査を実行します。MAILERとSiteverifyを差し替えるため、テストメールは送信しません。公開APIの確認にも、必須入力を欠いたリクエストを使ってください。

公開時はフォームを先に更新し、その後にWorkerをデプロイします。以前のページから認証なしで送信した場合は、再読み込みを案内します。
