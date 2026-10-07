<?php
session_start();
if (empty($_SESSION['authenticated'])) {
    header('Location: /index.php');
    exit;
}
$user = htmlspecialchars($_SESSION['username']);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Observ :: Dashboard</title>
    <style>
        body { font-family:-apple-system,Segoe UI,Roboto,sans-serif; background:#0f172a; color:#e2e8f0; margin:0; }
        header { background:#1e293b; padding:1rem 2rem; display:flex; justify-content:space-between; align-items:center; }
        .logo { color:#38bdf8; font-weight:700; }
        main { padding:2rem; max-width:720px; margin:0 auto; }
        .tile { background:#1e293b; border-radius:10px; padding:1.5rem; margin-bottom:1.25rem; }
        a.btn { display:inline-block; margin-top:.5rem; color:#38bdf8; text-decoration:none; }
        .muted { color:#64748b; font-size:.85rem; }
    </style>
</head>
<body>
    <header>
        <div class="logo">&#9680; Observ</div>
        <div class="muted">Signed in as <?php echo $user; ?> &middot; <a style="color:#f87171" href="/monitor/logout.php">logout</a></div>
    </header>
    <main>
        <div class="tile">
            <h2>Host Diagnostics</h2>
            <p class="muted">Run a connectivity check against a monitored host.</p>
            <a class="btn" href="/monitor/diag.php">Open diagnostics &rarr;</a>
        </div>
        <div class="tile">
            <h2>Monitored Hosts</h2>
            <p class="muted">web01 &middot; db01 &middot; cache01 &middot; gw01 &mdash; all nominal</p>
        </div>
        <div class="tile">
            <h2>Notes</h2>
            <p class="muted">Scheduled health checks are handled by the ops cron. See the devops notes table for the current runbook.</p>
        </div>
    </main>
</body>
</html>
