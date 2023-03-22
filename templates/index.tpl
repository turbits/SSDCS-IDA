% include("templates/includes/head.tpl")
<body>
  % include("templates/includes/nav.tpl")
  <div class="content">
    <h1>IDA System</h1>
    <ul>
      <!-- TODO: check for login status & remove login button/show dashboard button if logged in -->
      <li class="temp-list-item">
        <a href="/login" class="btn-primary br">User Login</a>
      </li>
      <li class="temp-list-item">
        <a href="/dashboard" class="btn-primary br">Dashboard</a>
      </li>
    </ul>
  </div>
</body>
