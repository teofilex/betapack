# Gunicorn podesavanja; gunicorn ih sam ucitava iz radnog foldera (railway.json i
# Procfile pokrecu "cd backend && gunicorn backend.wsgi ...").
#
# Bez ovoga gunicorn radi sa JEDNIM sinhronim workerom: zahtevi se obradjuju strogo
# jedan za drugim, pa jedan spor zahtev (upload slike na Cloudinary, slanje mejla,
# lista proizvoda) zaustavlja ceo API.
worker_class = 'gthread'
workers = 2          # dva procesa: pad ili restart jednog ne gasi API
threads = 4          # 8 istovremenih zahteva; DB/Cloudinary/Resend cekanja se preklapaju
timeout = 60         # upload slike na Cloudinary moze potrajati
graceful_timeout = 30
keepalive = 5
max_requests = 1000  # povremeno recikliranje procesa (curenje memorije)
max_requests_jitter = 100
