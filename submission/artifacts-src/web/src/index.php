<?php
session_start();
require_once __DIR__ . '/config.php';

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = isset($_POST['username']) ? $_POST['username'] : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';

    $conn = db_connect();

    // VULNERABLE (lab): user input is concatenated directly into the query,
    // allowing SQL injection / authentication bypass.
    $query = "SELECT id, username FROM users WHERE username = '$username' AND password = '$password'";
    $result = mysqli_query($conn, $query);

    if ($result && mysqli_num_rows($result) > 0) {
        $row = mysqli_fetch_assoc($result);
        $_SESSION['authenticated'] = true;
        $_SESSION['username'] = $row['username'];
        header('Location: /monitor/dashboard.php');
        exit;
    } else {
        $error = 'Invalid credentials.';
    }
    mysqli_close($conn);
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Observ :: Infrastructure Monitoring</title>
    <!-- Observ internal portal. Ops team: diagnostics moved under /monitor/ -->
    <style>
        body { font-family: -apple-system, Segoe UI, Roboto, sans-serif; background:#0f172a; color:#e2e8f0; display:flex; min-height:100vh; align-items:center; justify-content:center; margin:0; }
        .card { background:#1e293b; padding:2.5rem; border-radius:12px; width:320px; box-shadow:0 10px 40px rgba(0,0,0,.4); }
        h1 { font-size:1.4rem; margin:0 0 1.5rem; text-align:center; }
        .logo { color:#38bdf8; }
        label { display:block; font-size:.8rem; margin:.75rem 0 .25rem; color:#94a3b8; }
        input { width:100%; padding:.6rem; box-sizing:border-box; border:1px solid #334155; border-radius:6px; background:#0f172a; color:#e2e8f0; }
        button { width:100%; margin-top:1.25rem; padding:.65rem; border:0; border-radius:6px; background:#38bdf8; color:#0f172a; font-weight:600; cursor:pointer; }
        .error { color:#f87171; font-size:.85rem; margin-top:1rem; text-align:center; }
        .foot { text-align:center; font-size:.7rem; color:#475569; margin-top:1.5rem; }
    </style>
</head>
<body>
    <form class="card" method="post" action="/index.php">
        <h1><span class="logo">&#9680;</span> Observ</h1>
        <label for="username">Username</label>
        <input type="text" id="username" name="username" autocomplete="off" required>
        <label for="password">Password</label>
        <input type="password" id="password" name="password" required>
        <button type="submit">Sign in</button>
        <?php if ($error): ?><div class="error"><?php echo htmlspecialchars($error); ?></div><?php endif; ?>
        <div class="foot">Observ Monitoring v2.3 &middot; internal use only</div>
    </form>
</body>
</html>
