#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
提交 sitemap.xml 到 Google Search Console（Search Console API: sitemaps.submit）

为什么必须走 API
----------------
Google 已于 2023-06 正式弃用 Sitemaps ping 端点
(https://developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping)：
访问 google.com/ping?sitemap=... 现在直接返回 404 与
"Sitemaps ping is deprecated" 提示。唯一有效的主动通知方式是
Search Console API 的 sitemaps.submit（PUT）。

用法
----
1) 推荐：Service Account（可无人值守，自动化首选）
   前置：Google Cloud 启用 Search Console API -> 建 Service Account ->
        在 Search Console 把该 service account 邮箱加为「用户」（完整权限）->
        下载 JSON 密钥。
   设置环境变量后运行：
       set GSC_CLIENT_EMAIL=xxx@xxx.iam.gserviceaccount.com
       set GSC_PRIVATE_KEY=<JSON 里的 private_key 字段，含字面 \\n>
       python marketing/submit-to-google.py

2) 自检：校验 slug 在 sitemap 中恰好出现一次（不触网）
       python marketing/submit-to-google.py --check <slug>

3) 列出全部 sitemap 条目
       python marketing/submit-to-google.py --list

网络说明
--------
本机 Google 域名在境内常不可直连，需走本机代理。
默认读取环境变量 HTTPS_PROXY / HTTP_PROXY；
也可用 GSC_PROXY 显式指定，例如 http://127.0.0.1:7897。

重要提示
--------
- Indexing API 不可用于普通博客页。官方明确限定其仅支持
  JobPosting 与 BroadcastEvent(VideoObject) 类型页面，滥用会导致权限被撤。
  博客收录的正确路径是 sitemap 提交。
- lastmod 需反映"实质性修改"。每周新发博客写当天日期是准确的；
  不要为了"看起来新"而乱改旧页面的 lastmod，Google 会逐渐失去信任。
"""

import os
import sys
import argparse
import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET

SITE_URL = os.environ.get("GSC_SITE_URL", "sc-domain:minglulighting.com")
SITEMAP_URL = "https://minglulighting.com/sitemap.xml"
API_TMPL = "https://www.googleapis.com/webmasters/v3/sites/{site}/sitemaps/{feed}"

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
REPO_SITEMAP = os.path.join(REPO_ROOT, "sitemap.xml")


def _log(msg):
    print(msg, flush=True)


def _proxy_handler():
    """按 GSC_PROXY > HTTPS_PROXY > HTTP_PROXY 顺序构建 opener。"""
    proxy = os.environ.get("GSC_PROXY") or os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    if not proxy:
        return urllib.request.build_opener()
    handler = urllib.request.ProxyHandler({"https": proxy, "http": proxy})
    return urllib.request.build_opener(handler)


def read_sitemap_locals():
    if not os.path.exists(REPO_SITEMAP):
        raise SystemExit("ERROR: 找不到 %s" % REPO_SITEMAP)
    tree = ET.parse(REPO_SITEMAP)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [e.text.strip() for e in tree.getroot().findall("s:url/s:loc", ns) if e.text]
    return locs


def check_slug(slug):
    locs = read_sitemap_locals()
    target = "https://minglulighting.com/blog/%s.html" % slug
    hits = [l for l in locs if l.rstrip("/") == target.rstrip("/")]
    _log("sitemap 总条目: %d" % len(locs))
    _log("目标 %s 命中: %d" % (target, len(hits)))
    if len(set(locs)) != len(locs):
        _log("ERROR: sitemap 存在重复 <loc>")
        return False
    if len(hits) != 1:
        _log("ERROR: 目标条目数量应为 1")
        return False
    _log("OK: slug 校验通过")
    return True


def list_entries():
    for l in read_sitemap_locals():
        _log(l)
    return True


def _get_access_token():
    email = os.environ.get("GSC_CLIENT_EMAIL")
    key = os.environ.get("GSC_PRIVATE_KEY")
    if not email or not key:
        raise SystemExit(
            "ERROR: 缺少 GSC_CLIENT_EMAIL / GSC_PRIVATE_KEY。\n"
            "      首次配置步骤见本文件头部说明。\n"
            "      仅需自检可用:  python marketing/submit-to-google.py --check <slug>"
        )
    key = key.replace("\\n", "\n")
    try:
        from google.auth.transport.requests import Request
        from google.oauth2 import service_account
    except ImportError:
        raise SystemExit(
            "ERROR: 缺少依赖，请先安装:\n"
            "  pip install google-auth requests"
        )
    creds = service_account.Credentials.from_service_account_info(
        {"type": "service_account", "client_email": email, "private_key": key},
        scopes=["https://www.googleapis.com/auth/webmasters"],
    )
    creds.refresh(Request())
    return creds.token


def submit():
    token = _get_access_token()
    feed = urllib.parse.quote(SITEMAP_URL, safe="")
    site = urllib.parse.quote(SITE_URL, safe="")
    url = API_TMPL.format(site=site, feed=feed)
    _log("PUT %s" % url)
    req = urllib.request.Request(url, method="PUT")
    req.add_header("Authorization", "Bearer %s" % token)
    req.add_header("Content-Length", "0")
    try:
        with _proxy_handler().open(req, timeout=60) as r:
            _log("提交成功，状态: %s" % r.status)
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")[:800]
        _log("提交失败 HTTP %s: %s" % (e.code, e.reason))
        _log("响应: %s" % body)
        if e.code in (401, 403):
            _log("提示: 403 通常是 service account 邮箱未加入 Search Console 站点用户；"
                 "401 通常是密钥或 scope 问题。")
        return False
    except Exception as e:
        _log("提交异常: %s" % e)
        _log("提示: 国内网络访问 googleapis.com 常需代理，"
             "可设 GSC_PROXY=http://127.0.0.1:7897 后重试。")
        return False


def main():
    ap = argparse.ArgumentParser(description="提交 sitemap 到 Google Search Console")
    ap.add_argument("--check", metavar="SLUG", help="校验 slug 在 sitemap 中恰好出现一次")
    ap.add_argument("--list", action="store_true", help="列出全部 sitemap 条目")
    ap.add_argument("--submit", action="store_true", help="调用 Search Console API 提交")
    args = ap.parse_args()

    if args.check:
        sys.exit(0 if check_slug(args.check) else 1)
    if args.list:
        sys.exit(0 if list_entries() else 1)
    if args.submit:
        sys.exit(0 if submit() else 1)

    _log("未指定模式。可用: --check <slug> | --list | --submit")
    sys.exit(2)


if __name__ == "__main__":
    main()
