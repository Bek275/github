<?php
session_start();
if (empty($_SESSION['authenticated'])) {
    header('Location: /index.php');
    exit;
}

$output = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['host'])) {
    $host = $_POST['host'];

    // VULNERABLE (lab): the host parameter is passed unsanitized to a shell
    // command, allowing OS command injection (e.g. "8.8.8.8; id").
    $cmd = "ping -c 1 " . $host;
    $output = shell_exec($cmd . ' 2>&1');
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Observ :: Diagnostics</title>
    <style>
        body { font-family:-apple-system,Segoe UI,Roboto,sans-serif; background:#0f172a; color:#e2e8f0; margin:0; padding:2rem; }
        .wrap { max-width:720px; margin:0 auto; }
        input { padding:.6rem; border:1px solid #334155; border-radius:6px; background:#1e293b; color:#e2e8f0; width:320px; }
        button { padding:.6rem 1rem; border:0; border-radius:6px; background:#38bdf8; color:#0f172a; font-weight:600; cursor:pointer; }
        pre { background:#020617; padding:1rem; border-radius:8px; overflow:auto; white-space:pre-wrap; }
        a { color:#38bdf8; }
    </style>
</head>
<body>
    <div class="wrap">
        <p><a href="/monitor/dashboard.php">&larr; back</a></p>
        <h2>Host Diagnostics &mdash; connectivity check</h2>
        <form method="post" action="/monitor/diag.php">
            <input type="text" name="host" placeholder="e.g. 10.0.0.5" value="<?php echo isset($_POST['host']) ? htmlspecialchars($_POST['host']) : ''; ?>">
            <button type="submit">Ping</button>
        </form>
        <?php if ($output !== ''): ?>
            <h3>Result</h3>
            <pre><?php echo htmlspecialchars($output); ?></pre>
        <?php endif; ?>
    </div>
</body>
</html>
