Framework działa tak, że przeprowadza symulacje kilku epok na "urządzeniach" klientów, a potem agreguje rezultaty.

Istotne elementy:
- `pfl/algorithm/base.py:214` - algorithm.run gdzie wszystko się dzieje:
- `pfl/algorithm/base.py:271` - get_next_central_contexts wywoływany w pętli while True
- `pfl/algorithm/base.py:393` - warunek końca - get_next_central_contexts zwraca None jako central context
- side note, zmienna globalna _framework_module jako sideeffect

Jak tutaj wrzucić aspekty serverless:
- przepisać agregację (FederatedAveraging) żeby działała jako FaaS
    - `process_aggregated_statistics` zmodyfikować żeby robiła request na lambde i czekała na result (blokująco)
    - problem: agregacja robi bardzo mało, `pfl/algorithm/federated_averaging.py:28` - 2 linijki kodu, cała logika dzieje się w metodach modelu i statystyk (wag)
    - rozwiązanie - wysyłamy całe obiekty do lambdy - pickle (serializacja/deserializacja)    
- jak mamy wagi z klientów (step 2), to wysyłamy je na lambde
- problem: PFL daje nam wagi wszystkich klientów naraz, ale tu możemy zasymulować opóźnienia
 
tylko że mamy tutaj tylko jedną funkcje i wszystkie potrzebne dane możemy jej wysłać przez POST, jaka tu ma być komunikacja? "klienci" są symulowani lokalnie. 

Druga opcja:
  * backend ma metodę `async_gather_results`, która trenuje modele u klientów    
  * klienci mogą być w funkcjach serverless, zamiast wysyłać model do każdego to mamy centralny model w redisie/s3/whatever i lambdy klientów i lambda do agregacji go pobierają




important:
żeby odpalić notebooka:
'export PYTHONPATH=`pwd`:$PYTHONPATH'

