% include("templates/includes/head.tpl")
% include("templates/includes/nav.tpl")

<div class="content">
  <h1>IDA System</h1>
  % if session_uuid is not None and username is not None:
    <h2>Welcome to IDA, {{username}}</h2>
      <form action="/dashboard" method="GET">
        <button class="btn-primary br" type="submit">Dashboard</button>
      </form>
  % else:
    <h2>Please log in</h2>
    <form action="/login" method="GET">
      <button class="btn-primary br" type="submit">Login</button>
    </form>

  % if error is not None:
    <p class="error-message">{{error}}</p>
  % end

  % if success is not None:
    <p class="success-message">{{success}}</p>
  % end
</div>
