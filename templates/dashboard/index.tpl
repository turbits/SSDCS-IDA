% from bottle import request, redirect, template

% include("templates/includes/head.tpl")
% include("templates/includes/nav.tpl")

<div class="content">
    <h1>IDA System Dashboard</h1>

    <a href="/dashboard" class="btn-primary br">Refresh</a>


    % if session_uuid is not None and username is not None:
        % if data is not None:
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Created At</th>
                        <th>Revised At</th>
                        <th>File</th>
                    </tr>
                </thead>
                <tbody>
                    % for row in data:
                        <tr>
                            <td>{{row[0]}}</td>
                            <td>{{row[1]}}</td>
                            <td>{{row[2]}}</td>
                            <td>{{row[3]}}</td>
                            <td>{{row[4]}}</td>
                            <td>
                                <a href="#">Edit</a>
                                <a href="#">Delete</a>
                            </td>
                        </tr>
                    % end
                </tbody>
            </table>
        % else:
            <p class="info-message br">No data found.</p>
        % end
    % else:
        % template('templates/login/index.tpl', success=None, error='You are not logged in.')
    % end

    % if error is not None:
        <p class="error-message br">{{error}}</p>
    % end

    % if success is not None:
        <p class="success-message br">{{success}}</p>
    % end
</div>
