% from bottle import request, redirect

% include("templates/includes/head.tpl")
% include("templates/includes/nav.tpl")

<div class="content">
    <h1>IDA System Login</h1>

    % if session_uuid is not None and username is not None:
        % redirect('/')
    % else:
        <div class="content">
            <form class="flex-form" action="/login" method="POST">
                <input class="br" type="text" name="username" placeholder="Username">
                <input class="br" type="password" name="password" placeholder="Password">
                <input class="br" type="submit" value="Login">
            </form>
        </div>
    % end

    % if error is not None:
        <p class="error-message">{{error}}</p>
    % end

    % if success is not None:
        <p class="success-message">{{success}}</p>
    % end
</div>
