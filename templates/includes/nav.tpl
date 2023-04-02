<nav>
    <span class="nav-item text-display"><a href="/" class="nav-title">IDA</a></span>
    % if username is not None:
      <div class="nav-item nav-item-container">
        <p class="nav-item nav-profile br nocursor">{{username}}</p>
        <a href="/logout" class="nav-item nav-link btn-primary-rev br">Logout</a>
      <div>
    % end
  </ul>
</nav>
