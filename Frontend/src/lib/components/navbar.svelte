<header class="navbar-header">
  <nav class="navbar">
    <div class="navbar-brand">
      <a href="/">osu!Oracle</a>
    </div>

    <div class="navbar-links">
      <a
        href="https://github.com/MichaelDeng03/osu_oracle"
        target="_blank"
        class="nav-link github"
        aria-label="GitHub Repository"
        title="GitHub Repository"
      >
        <i class="fa-brands fa-github fa-lg"></i>
      </a>
      <a href="/login" class="nav-link login-btn">Login</a>
    </div>
  </nav>
</header>

<style>
  /* --- Layout & Containers --- */
  .navbar-header {
    background-color: #333;
    color: white;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 1000;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 20px;
    margin: 0 auto;
  }

  .navbar-links {
    display: flex;
    align-items: center;
  }

  .navbar-brand a {
    color: white;
    text-decoration: none;
    font-size: 1.5em;
    font-weight: bold;
  }

  .nav-link {
    color: #ccc;
    text-decoration: none;
    padding: 8px 15px;
    margin-left: 15px;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
  }

  .nav-link:hover {
    color: white;
  }

  .github {
    font-size: 1.25em;
  }

  .login-btn {
    background-color: #007bff;
    color: white;
    border-radius: 5px;
    font-weight: bold;
  }

  .login-btn:hover {
    background-color: #0056b3;
    color: white;
    transform: translateY(-1px);
  }
</style>
