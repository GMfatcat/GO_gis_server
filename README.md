### GO_gis_server
    
- [x] Generate Massive Fake Data (2023/4/4)
- [x] GO calculate GIS Index (2023/4/8)
- [x] GO connect to Redis for cache and temporary storage
- [ ] Construct Simple Web Page for Visualizations
- [ ] Integrate GO server with DB and Web Page
- [ ] TBD

    
1. FINISH MULTI-PROCESSING GENERATE FAKE DATA in 9.81 min : 526 MB / 3,769,343 files in 120 folders    
2. Finish GIS GRID INDEX CALCULATION: Solve import modules in Test directory    
3. Calculate and Save binary data of batch_1 in 0.5 ~ 0.6 seconds    
4. Add simple redis connection: save simple Grid data for 10 seconds(local test)    
5. Finish All GIS GRID SUM save to redis(expire time is controlable now, now set to 10 sec)    

Redis-Server Commands
```=
// RUN with cmd , not powershell
redis-server --service-start
redis-server --service-stop
// check connection
redis-cli ping
// version
redis-cli --version
```

:point_right: I use Redis for Windows version 5.0.14.1