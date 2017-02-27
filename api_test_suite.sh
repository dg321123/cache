#!/bin/bash

PORT=${1:-7101}
BASE_URL="http://127.0.0.1:$PORT"

echo $PORT
echo $BASE_URL

for TOOL in bc curl jq wc awk sort uniq tr head tail; do
    if ! which $TOOL >/dev/null; then
        echo "ERROR: $TOOL is not available in the PATH"
        exit 1
    fi
done

PASS=0
FAIL=0
TOTAL=0

function describe() {
    echo -n "$1"; let TOTAL=$TOTAL+1
}

function pass() {
    echo "pass"; let PASS=$PASS+1
}

function fail() {
    echo "fail";  let FAIL=$FAIL+1
}

function report() {
    PCT=$(echo "scale=2; $PASS / $TOTAL * 100" |bc)
    echo "$PASS/$TOTAL ($PCT%) tests passed"
}

describe "test-01-01: healthcheck = "

ATTEMPTS=0
while true; do
    let ATTEMPTS=$ATTEMPTS+1
    echo "Attempt $ATTEMPTS"
    RESPONSE=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/healthcheck")
    if [[ $RESPONSE == "200" ]]; then
        let TIME=$ATTEMPTS*15
        echo -n "($TIME seconds) "; pass
        break
    else
        if [[ $ATTEMPTS -gt 24 ]]; then
            let TIME=$ATTEMPTS*15
            echo -n "($TIME seconds) "; fail
            break
        fi
        #sleep 1
    fi
done

describe "test-02-01: / key count = "

COUNT=$(curl -s "$BASE_URL" |jq -r 'keys |.[]' |wc -l |awk '{print $1}')

if [[ $COUNT -eq 31 ]]; then
    pass
else
    echo "[$COUNT]"
    fail
fi

describe "test-02-02: / repository_search_url value = "

VALUE=$(curl -s "$BASE_URL" |jq -r '.repository_search_url')

if [[ "$VALUE" == "https://api.github.com/search/repositories?q={query}{&page,per_page,sort,order}" ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-02-03: / organization_repositories_url value = "

VALUE=$(curl -s "$BASE_URL" |jq -r '.organization_repositories_url')

if [[ "$VALUE" == "https://api.github.com/orgs/{org}/repos{?type,page,per_page,sort}" ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-03-01: /orgs/Netflix key count = "

COUNT=$(curl -s "$BASE_URL/orgs/Netflix" |jq -r 'keys |.[]' |wc -l |awk '{print $1}')

if [[ $COUNT -eq 24 ]]; then
    pass
else
    echo "[$COUNT]"
    fail
fi

describe "test-03-02: /orgs/Netflix avatar_url = "

VALUE=$(curl -s "$BASE_URL/orgs/Netflix" |jq -r '.avatar_url')

if [[ "$VALUE" == "https://avatars.githubusercontent.com/u/913567?v=3" ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-03-03: /orgs/Netflix location = "

VALUE=$(curl -s "$BASE_URL/orgs/Netflix" |jq -r '.location')

if [[ "$VALUE" == "Los Gatos, California" ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-04-01: /orgs/Netflix/members object count = "

COUNT=$(curl -s "$BASE_URL/orgs/Netflix/members" |jq -r '. |length')

if [[ $COUNT -gt 40 ]] && [[ $COUNT -lt 57 ]]; then
    pass
else
    echo "[$COUNT]"
    fail
fi

describe "test-04-02: /orgs/Netflix/members login first alpha case-insensitive = "

VALUE=$(curl -s "$BASE_URL/orgs/Netflix/members" |jq -r '.[] |.login' |tr '[:upper:]' '[:lower:]' |sort |head -1)

if [[ "$VALUE" == "aglover" ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-04-03: /orgs/Netflix/members login first alpha case-sensitive = "

    VALUE=$(curl -s "$BASE_URL/orgs/Netflix/members" |jq -r '.[] |.login' |sort |head -37| tail -1)

if [[ "$VALUE" == "ScottMansfield" ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-04-04: /orgs/Netflix/members login last alpha case-insensitive = "

VALUE=$(curl -s "$BASE_URL/orgs/Netflix/members" |jq -r '.[] |.login' |tr '[:upper:]' '[:lower:]' |sort |tail -1)

if [[ "$VALUE" == "zethussuen" ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-04-05: /orgs/Netflix/members id first = "

VALUE=$(curl -s "$BASE_URL/orgs/Netflix/members" |jq -r '.[] |.id' |sort -n |head -1)

if [[ "$VALUE" == "21094" ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-04-06: /orgs/Netflix/members id last = "

VALUE=$(curl -s "$BASE_URL/orgs/Netflix/members" |jq -r '.[] |.id' |sort -n |tail -1)

if [[ "$VALUE" == "13667833" ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-04-07: /users/aglover/orgs proxy = "

VALUE=$(curl -s "$BASE_URL/users/aglover/orgs" |jq -r '.[] |.login' |tr -d '\n')

if [[ "$VALUE" == "FoklNetflixhubot-scripts" ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-04-08: /users/zethussuen/orgs proxy = "

VALUE=$(curl -s "$BASE_URL/users/zethussuen/orgs" |jq -r '.[] |.login' |tr -d '\n')

if [[ "$VALUE" == "Netflix" ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-05-01: /orgs/Netflix/repos object count = "

COUNT=$(curl -s "$BASE_URL/orgs/Netflix/repos" |jq -r '. |length')

if [[ $COUNT -gt 113 ]] && [[ $COUNT -lt 125 ]]; then
    pass
else
    echo "[$COUNT]"
    fail
fi

describe "test-05-02: /orgs/Netflix/repos full_name first alpha case-insensitive = "

VALUE=$(curl -s "$BASE_URL/orgs/Netflix/repos" |jq -r '.[] |.full_name' |tr '[:upper:]' '[:lower:]' |sort |head -1)

if [[ "$VALUE" == "netflix/aegisthus" ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-05-03: /orgs/Netflix/members full_name first alpha case-sensitive = "

VALUE=$(curl -s "$BASE_URL/orgs/Netflix/repos" |jq -r '.[] |.full_name' |sort |head -1)

if [[ "$VALUE" == "Netflix/aegisthus" ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-05-04: /orgs/Netflix/members login last alpha case-insensitive = "

VALUE=$(curl -s "$BASE_URL/orgs/Netflix/repos" |jq -r '.[] |.full_name' |tr '[:upper:]' '[:lower:]' |sort |tail -1)

if [[ "$VALUE" == "netflix/zuul" ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-05-05: /orgs/Netflix/repos id first = "

VALUE=$(curl -s "$BASE_URL/orgs/Netflix/repos" |jq -r '.[] |.id' |sort -n |head -1)

if [[ "$VALUE" == "2044029" ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-05-06: /orgs/Netflix/repos id last = "

VALUE=$(curl -s "$BASE_URL/orgs/Netflix/repos" |jq -r '.[] |.id' |sort -n |tail -1)

if [[ "$VALUE" == "81116742" ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-05-07: /orgs/Netflix/repos languages unique = "

VALUE=$(curl -s "$BASE_URL/orgs/Netflix/repos" |jq -r '.[] |.language' |sort -u |tr -d '\n')

if [[ "$VALUE" == "CC#C++ClojureGoGroovyHTMLJavaJavaScriptNginxnullPythonRubyScalaShell" ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi



describe "test-06-01: /view/top/5/forks = "

VALUE=$(curl -s "$BASE_URL/view/top/5/forks" | tr -d '[:space:]\n')

if [[ "$VALUE" == '[["Netflix/Hystrix",1695],["Netflix/SimianArmy",703],["Netflix/eureka",676],["Netflix/zuul",536],["Netflix/Cloud-Prize",520]]' ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-06-01: /view/top/10/forks = "

VALUE=$(curl -s "$BASE_URL/view/top/10/forks" | tr -d '[:space:]\n')

if [[ "$VALUE" == '[["Netflix/Hystrix",1695],["Netflix/SimianArmy",703],["Netflix/eureka",676],["Netflix/zuul",536],["Netflix/Cloud-Prize",520],["Netflix/asgard",426],["Netflix/astyanax",359],["Netflix/curator",359],["Netflix/ice",345],["Netflix/ribbon",317]]' ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-06-01: /view/top/5/last_updated = "

VALUE=$(curl -s "$BASE_URL/view/top/5/last_updated" | tr -d '[:space:]\n')

if [[ "$VALUE" == '[["Netflix/stethoscope","2017-02-27T05:32:03Z"],["Netflix/blitz4j","2017-02-27T05:25:46Z"],["Netflix/servo","2017-02-27T05:25:23Z"],["Netflix/archaius","2017-02-27T05:25:00Z"],["Netflix/Hystrix","2017-02-27T05:24:31Z"]]' ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-06-01: /view/top/10/last_updated = "

VALUE=$(curl -s "$BASE_URL/view/top/10/last_updated" | tr -d '[:space:]\n')

if [[ "$VALUE" == '[["Netflix/stethoscope","2017-02-27T05:32:03Z"],["Netflix/blitz4j","2017-02-27T05:25:46Z"],["Netflix/servo","2017-02-27T05:25:23Z"],["Netflix/archaius","2017-02-27T05:25:00Z"],["Netflix/Hystrix","2017-02-27T05:24:31Z"],["Netflix/ribbon","2017-02-27T05:24:19Z"],["Netflix/karyon","2017-02-27T05:23:52Z"],["Netflix/zuul","2017-02-27T05:23:32Z"],["Netflix/eureka","2017-02-27T05:22:54Z"],["Netflix/chaosmonkey","2017-02-27T05:01:01Z"]]' ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-06-01: /view/top/5/open_issues = "

VALUE=$(curl -s "$BASE_URL/view/top/5/open_issues"  | tr -d '[:space:]\n')

if [[ "$VALUE" == '[["Netflix/astyanax",158],["Netflix/ribbon",115],["Netflix/ice",108],["Netflix/asgard",103],["Netflix/falcor",93]]' ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-06-01: /view/top/10/open_issues = "

VALUE=$(curl -s "$BASE_URL/view/top/10/open_issues" | tr -d '[:space:]\n')

if [[ "$VALUE" == '[["Netflix/astyanax",158],["Netflix/ribbon",115],["Netflix/ice",108],["Netflix/asgard",103],["Netflix/falcor",93],["Netflix/Hystrix",72],["Netflix/security_monkey",67],["Netflix/zuul",64],["Netflix/archaius",50],["Netflix/governator",43]]' ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-06-01: /view/top/5/stars = "

VALUE=$(curl -s "$BASE_URL/view/top/5/stars"  | tr -d '[:space:]\n')

if [[ "$VALUE" == '[["Netflix/Hystrix",8560],["Netflix/falcor",7445],["Netflix/SimianArmy",5131],["Netflix/eureka",2919],["Netflix/vector",2205]]' ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-06-01: /view/top/10/stars = "

VALUE=$(curl -s "$BASE_URL/view/top/10/stars" | tr -d '[:space:]\n')

if [[ "$VALUE" == '[["Netflix/Hystrix",8560],["Netflix/falcor",7445],["Netflix/SimianArmy",5131],["Netflix/eureka",2919],["Netflix/vector",2205],["Netflix/zuul",2173],["Netflix/asgard",2143],["Netflix/ice",2118],["Netflix/Scumblr",1960],["Netflix/chaosmonkey",1887]]' ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-06-01: /view/top/5/watchers = "

VALUE=$(curl -s "$BASE_URL/view/top/5/watchers" | tr -d '[:space:]\n')

if [[ "$VALUE" == '[["Netflix/Hystrix",8560],["Netflix/falcor",7445],["Netflix/SimianArmy",5131],["Netflix/eureka",2919],["Netflix/vector",2205]]' ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

describe "test-06-01: /view/top/10/watchers = "

VALUE=$(curl -s "$BASE_URL/view/top/10/watchers" | tr -d '[:space:]\n')

if [[ "$VALUE" == '[["Netflix/Hystrix",8560],["Netflix/falcor",7445],["Netflix/SimianArmy",5131],["Netflix/eureka",2919],["Netflix/vector",2205],["Netflix/zuul",2173],["Netflix/asgard",2143],["Netflix/ice",2118],["Netflix/Scumblr",1960],["Netflix/chaosmonkey",1887]]' ]]; then
    pass
else
    echo "[$VALUE]"
    fail
fi

report
