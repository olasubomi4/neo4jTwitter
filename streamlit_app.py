# streamlit_app.py
import os
import json
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Tweet & User Recommender", layout="wide")

st.title("Twitter Graph Recommender – Streamlit Client")

# --- Config panel
with st.sidebar:
    st.header("Settings")
    default_base = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")
    base_url = st.text_input("API base URL", value=default_base, help="Your Flask server origin.")
    timeout = st.number_input("Request timeout (seconds)", min_value=1, max_value=60, value=15)
    st.markdown("---")
    st.caption("Powered by  Flask + My Neo4j recommender API")

# --- Endpoint selector & input
mode = st.radio(
    "Choose what to do",
    [
        "Tweets to a user",
        "Users to follow",
        "Top communities",
        "Top users",
    ],
    horizontal=True,
)
placeholder_user="MySQL"
# Default endpoint + inputs per mode
if mode == "Tweets to a user":
    endpoint = "/recommendTweetsToUser"
    http_method = "POST"
    placeholder_user = "rotnroll666"
elif mode == "Users to follow":
    endpoint = "/recommendUser"
    http_method = "POST"
    placeholder_user = "MySQL"
elif mode == "Top communities":
    endpoint = "/communities"
    http_method = "GET"
else:
    endpoint = "/user"
    http_method = "GET"

# --- Inputs common/specific
params = {}
body = {}

if mode in ("Tweets to a user", "Users to follow"):
    user_name = st.text_input(
        "Twitter handle / Screen name",
        value=placeholder_user,
        help="Value sent as 'userName' in the POST body.",
    )
    body = {"userName": user_name}

elif mode == "Top users":
    c1, c2 = st.columns(2)
    with c1:
        limit = st.number_input("Limit", min_value=1, max_value=500, value=10, step=1)
    with c2:
        sort = st.selectbox("Sort by", ["Popularity", "Importance", "Influence"], index=0,
                            help="Accepted values: Popularity, Importance, Influence")
    params = {"limit": int(limit), "sort": sort}

# Action button
col1, col2 = st.columns([1, 3])
with col1:
    go = st.button(" Fetch", use_container_width=True)
with col2:
    st.write("")

# --- Helpers

def request_json(method: str, base_url: str, path: str, timeout_s: int, *, params=None, json_body=None):
    url = base_url.rstrip("/") + path
    try:
        if method.upper() == "GET":
            resp = requests.get(url, params=params or {}, timeout=timeout_s)
        else:
            headers = {"Content-Type": "application/json"}
            resp = requests.post(url, params=params or {}, data=json.dumps(json_body or {}), headers=headers, timeout=timeout_s)
        try:
            data = resp.json()
        except Exception:
            data = {"responseStatus": False, "responseMessage": f"Non-JSON response (HTTP {resp.status_code})", "raw": resp.text}
        return resp.status_code, data
    except requests.RequestException as e:
        return 0, {"responseStatus": False, "responseMessage": f"Request error: {e}"}

@st.cache_data(show_spinner=False)
def fetch_cached(method, base_url, path, timeout_s, params, json_body):
    return request_json(method, base_url, path, timeout_s, params=params, json_body=json_body)

# --- Action
if go:
    with st.spinner("Contacting API…"):
        status_code, data = fetch_cached(http_method, base_url, endpoint, timeout, params, body)

    ok = bool(data.get("responseStatus"))
    msg = data.get("responseMessage", "")

    top = st.container()
    if ok:
        top.success(f"{msg} (HTTP {status_code})")
    else:
        top.error(f"{msg or 'Request failed'} (HTTP {status_code})")
        if "raw" in data:
            with st.expander("Raw response"):
                st.code(str(data["raw"]))

    body_json = data.get("responseBody", [])

    # Branch on response shapes per mode
    if ok:
        if mode in ("Tweets to a user", "Users to follow") and isinstance(body_json, list):
            # Detect tweet-recommendation shape
            is_tweet_shape = all(isinstance(x, dict) and ("Tweet" in x or "similarTweets" in x) for x in body_json)
            if is_tweet_shape:
                st.subheader("Recommended Tweets")
                for i, item in enumerate(body_json, start=1):
                    tweet_text = item.get("Tweet", "<no tweet>")
                    scores = item.get("SimilarityScores", [])
                    similar = item.get("similarTweets", []) or []
                    avg = sum(scores) / len(scores) if scores else None

                    with st.container(border=True):
                        cols = st.columns([6, 2])
                        with cols[0]:
                            st.markdown(f"**{i}.** {tweet_text}")
                        with cols[1]:
                            if avg is not None:
                                st.metric("Avg similarity", f"{avg:.3f}")
                        if similar:
                            with st.expander("View similar tweets"):
                                for s in similar:
                                    st.write("• ", s)

                # Table + export
                flat = []
                for item in body_json:
                    flat.append({
                        "Tweet": item.get("Tweet", ""),
                        "AvgSimilarity": (sum(item.get("SimilarityScores", [])) / len(item.get("SimilarityScores", [])) if item.get("SimilarityScores") else None),
                        "SimilarTweets": " \n".join(item.get("similarTweets", []) or []),
                    })
                df = pd.DataFrame(flat)
                st.markdown("### Table view")
                st.dataframe(df, use_container_width=True)
                st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), file_name="tweet_recs.csv", mime="text/csv")

            else:
                # Assume user-recommendation shape
                st.subheader("Recommended Users to Follow")
                rows = []
                for item in body_json:
                    rows.append({
                        "Name": item.get("recommededUserName") or item.get("recommendedUserName"),
                        "ScreenName": item.get("recommededUserScreenName") or item.get("recommendedUserScreenName"),
                        "PageRank": item.get("PageRank"),
                    })
                dfu = pd.DataFrame(rows).sort_values("PageRank", ascending=False, na_position="last")
                def to_link(handle):
                    if isinstance(handle, str) and handle:
                        return f"https://x.com/{handle}"
                    return None
                dfu["Profile"] = dfu["ScreenName"].map(to_link)
                st.dataframe(dfu, use_container_width=True)
                st.download_button("Download CSV", dfu.to_csv(index=False).encode("utf-8"), file_name="user_recs.csv", mime="text/csv")
                st.markdown("#### Quick actions")
                for _, r in dfu.head(10).iterrows():
                    with st.container(border=True):
                        pr = r["PageRank"]
                        pr_str = f"{pr:.4f}" if isinstance(pr, (int, float)) else str(pr)
                        st.markdown(f"**{r['Name']}**  `@{r['ScreenName']}`  • PageRank: **{pr_str}**")
                        if r["Profile"]:
                            st.link_button("Open profile", r["Profile"], use_container_width=False)

        elif mode == "Top communities" and isinstance(body_json, list):
            st.subheader("Top Communities")
            # Summary table
            summary_rows = []
            for item in body_json:
                cid = item.get("communityId")
                members = item.get("members", []) or []
                summary_rows.append({"communityId": cid, "membersCount": len(members)})
            dfc = pd.DataFrame(summary_rows).sort_values("membersCount", ascending=False)
            st.dataframe(dfc, use_container_width=True)
            st.download_button("Download summary CSV", dfc.to_csv(index=False).encode("utf-8"), file_name="communities_summary.csv", mime="text/csv")

            # Detailed view
            st.markdown("### Details")
            for item in body_json:
                cid = item.get("communityId")
                members = item.get("members", []) or []
                with st.container(border=True):
                    st.markdown(f"**Community {cid}** · {len(members)} members")
                    with st.expander("Show members"):
                        dfm = pd.DataFrame({"member": members})
                        st.dataframe(dfm, use_container_width=True, hide_index=True)

            # One CSV with exploded members
            exploded = []
            for item in body_json:
                for m in item.get("members", []) or []:
                    exploded.append({"communityId": item.get("communityId"), "member": m})
            dfx = pd.DataFrame(exploded)
            st.download_button("Download all members CSV", dfx.to_csv(index=False).encode("utf-8"), file_name="communities_members.csv", mime="text/csv")

        elif mode == "Top users" and isinstance(body_json, list):
            st.subheader("Top Users")
            rows = [{"score": it.get("score"), "userName": it.get("userName")} for it in body_json]
            dftu = pd.DataFrame(rows)
            st.dataframe(dftu, use_container_width=True)
            st.download_button("Download CSV", dftu.to_csv(index=False).encode("utf-8"), file_name="top_users.csv", mime="text/csv")

    elif go and ok and not body_json:
        st.info("No data returned.")

    # Debug panel
    with st.expander("Debug: raw JSON"):
        st.code(json.dumps(data, indent=2))

# --- Footer
st.markdown("---")
st.caption("Tip: set an environment variable `API_BASE_URL` so teammates don't have to edit the code.")