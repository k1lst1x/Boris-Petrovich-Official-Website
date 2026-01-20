(function () {
  const modal = document.getElementById("modal-contact");
  const openers = document.querySelectorAll('[data-modal-open="contact"]');
  const closers = document.querySelectorAll('[data-modal-close="contact"]');

  function openModal() {
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  openers.forEach((b) => b.addEventListener("click", (e) => { e.preventDefault(); openModal(); }));
  closers.forEach((b) => b.addEventListener("click", (e) => { e.preventDefault(); closeModal(); }));

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("is-open")) closeModal();
  });

  // FAQ accordion
  document.querySelectorAll(".acc").forEach((item) => {
    const head = item.querySelector(".acc__head");
    if (!head) return;
    head.addEventListener("click", () => {
      item.classList.toggle("is-open");
    });
  });

  // Partners slider
  const track = document.querySelector('[data-slider-track="partners"]');
  const leftBtn = document.querySelector('[data-slider-left="partners"]');
  const rightBtn = document.querySelector('[data-slider-right="partners"]');

  function scrollByAmount(dir) {
    if (!track) return;
    const amount = 320;
    track.scrollBy({ left: dir * amount, behavior: "smooth" });
  }

  if (leftBtn) leftBtn.addEventListener("click", () => scrollByAmount(-1));
  if (rightBtn) rightBtn.addEventListener("click", () => scrollByAmount(1));

  // Submit form (AJAX, чтобы красиво)
  const form = document.getElementById("contactForm");
  const hint = document.getElementById("contactFormHint");

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (hint) hint.textContent = "";

      const formData = new FormData(form);

      try {
        const res = await fetch(form.action, {
          method: "POST",
          headers: { "X-Requested-With": "XMLHttpRequest" },
          body: formData,
        });

        const data = await res.json();
        if (data.ok) {
          if (hint) hint.textContent = "Отправлено. Мы свяжемся с вами.";
          form.reset();
          setTimeout(() => closeModal(), 700);
        } else {
          if (hint) hint.textContent = data.error || "Ошибка отправки.";
        }
      } catch (err) {
        if (hint) hint.textContent = "Сеть/сервер: ошибка отправки.";
      }
    });
  }
})();
