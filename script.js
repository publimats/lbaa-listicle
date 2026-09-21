(() => {
  const incoming = new URLSearchParams(window.location.search);

  document.querySelectorAll("a.shop-link").forEach((link) => {
    const destination = new URL(link.href);

    incoming.forEach((value, key) => {
      if (!destination.searchParams.has(key)) {
        destination.searchParams.set(key, value);
      }
    });

    const position = link.dataset.ctaPosition;
    if (position) {
      destination.searchParams.set("cta_position", position);
    }

    link.href = destination.toString();
  });
})();
