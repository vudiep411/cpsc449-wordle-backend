# game: hypercorn wordle --reload --debug --bind books.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG
user: hypercorn user --reload --debug --bind books.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG

# game1: hypercorn wordle --reload --debug --bind books.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG
# game2: hypercorn wordle --reload --debug --bind books.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG
# game3: hypercorn wordle --reload --debug --bind books.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG

leaderboard: hypercorn leaderboard --reload --debug --bind books.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG

primary: ./bin/litefs -config ./etc/primary.yml 
secondary1: ./bin/litefs -config ./etc/secondary1.yml
secondary2: ./bin/litefs -config ./etc/secondary2.yml





