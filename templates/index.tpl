% include("templates/includes/head.tpl")
% include("templates/includes/nav.tpl")

<div class="content">
  <h1>IDA System</h1>
  % if session_uuid is not None and username is not None:
    <h2>Welcome, {{username}}</h2>
      <a href="/dashboard" class="btn-primary br">Dashboard</a>
  % else:
    <h2>Please log in</h2>
    <a href="/login" class="btn-primary br">Login</a>
  % end

  % if error is not None:
    <p class="error-message">{{error}}</p>
  % end

  % if success is not None:
    <p class="success-message">{{success}}</p>
  % end
</div>
