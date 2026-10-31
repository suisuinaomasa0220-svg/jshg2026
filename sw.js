// 最小のService Worker（Chromeの「アプリとしてインストール」条件を満たすため）。キャッシュはしない＝常に最新を表示
self.addEventListener('install',e=>self.skipWaiting());
self.addEventListener('activate',e=>self.clients.claim());
self.addEventListener('fetch',e=>{});
