<script>
  import { onMount } from "svelte";
  import Nav from "$lib/components/navbar.svelte";
  let apiMessage = "Loading...";

  onMount(async () => {
    try {
      const response = await fetch("http://localhost:8000/");

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      apiMessage = data.message;
    } catch (error) {
      console.error("Error fetching data:", error);
      apiMessage =
        "Failed to connect to API. Check backend server and CORS config.";
    }
  });
</script>

<Nav />
<slot />
<main>
  <h1>Welcome to SvelteKit</h1>
  <p>API Response from FastAPI: <strong>{apiMessage}</strong></p>
</main>
