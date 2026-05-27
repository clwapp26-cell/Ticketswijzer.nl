import html
def esc(s): return html.escape(str(s), quote=True)

COOKIE_BAR = """<div id="cookiebar" style="display:none">
  <span>Wij gebruiken cookies voor een goede werking van de site en voor affiliate-links. <a href="__ROOT__cookiebeleid.html">Meer info</a>.</span>
  <span class="cb-btns"><button type="button" id="cb-ok">Akkoord</button><button type="button" id="cb-no">Weigeren</button></span>
</div>
<script>
(function(){try{if(!localStorage.getItem('tw_cookie')){var b=document.getElementById('cookiebar');b.style.display='flex';var c=function(v){try{localStorage.setItem('tw_cookie',v)}catch(e){}b.style.display='none'};document.getElementById('cb-ok').onclick=function(){c('akkoord')};document.getElementById('cb-no').onclick=function(){c('geweigerd')};}}catch(e){}})();
</script>"""

def foot(root, site):
    return f"""<footer><div class="wrap footer-flex">
  <div><strong>{esc(site['name'])}</strong> — vergelijk &amp; bespaar op dagjes uit in Nederland</div>
  <div class="foot-links"><a href="{root}over-ons.html">Over ons</a> · <a href="{root}contact.html">Contact</a> · <a href="{root}privacybeleid.html">Privacybeleid</a> · <a href="{root}cookiebeleid.html">Cookiebeleid</a></div>
  <div>{esc(site['domain'])} · richtprijzen, controleer bij de aanbieder · bevat affiliate-links</div>
</div></footer>
{COOKIE_BAR.replace("__ROOT__", root)}
</body></html>"""

def head(*a, **k): return "<html><head></head><body>"

pages=[{"slug":"over-ons","title":"T","description":"D","h1":"Over ons","body":"<p>x</p>"}]
site={"name":"TicketsWijzer","domain":"ticketswijzer.nl"}
for p in pages:
    page = head() + f"""
<section class="hero slim"><div class="wrap">
  <div class="crumb"><a href="index.html">Home</a> › {esc(p['h1'])}</div>
  <h1>{esc(p['h1'])}</h1>
</div></section>
<main class="wrap detail-body">
  <article class="gids">
{p['body']}
  </article>
</main>
""" + foot("", site)
print("page-loop OK:", len(page), "| cookiebar:", "cookiebar" in page, "| footlinks:", "over-ons.html" in page)
print("foot root ../ OK:", "../cookiebeleid.html" in foot("../", site))
