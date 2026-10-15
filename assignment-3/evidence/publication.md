# Publication verification · October 15, 2026

- Authorization: student selected “Push the Part 3.1 branch,” then wrote “make sure the repo is public.”
- Destination: [ben-randall1/IST-402-assignment-1](https://github.com/ben-randall1/IST-402-assignment-1), branch [codex/assignment-3-part-1](https://github.com/ben-randall1/IST-402-assignment-1/tree/codex/assignment-3-part-1).
- Git rejected the saved username/token. The connected GitHub account had repository administration/push access and published the approved snapshot through GitHub's Git-object API. No connector credential was extracted or stored locally.
- All 57 changed/new blobs were checked against their local Git object hashes. The resulting remote tree `b3d38800af704cea48a20831883440d0d8114421` exactly matched local commit `cc56d5c`'s tree.
- Published design checkpoint: `744fca701d4446db1ea0c7f4a9a4565954ce587c`. API publication produces a new commit identity while preserving the complete reviewed file tree. The original local history remains on `codex/assignment-3-local-history`.
- GitHub metadata already reported `visibility=public`. An independent anonymous HTTP request to GitHub's repository API confirmed `private=false`, `visibility=public`, and the branch head at the published checkpoint. No visibility change was necessary.
- Before publication/public-access verification, local reachable history (253 objects) was checked for configured credential values, common credential/private-key patterns, and tracked root `.env`/working `data/*.db`; no matches were found. This bounded check does not claim an exhaustive sensitive-data audit.
- Root `report.md` was updated with the public assessed commit, absolute pinned artifact links, and current status. The report/publication metadata follow the design checkpoint in a separate commit.
- No prototype deployment, invitation to use it for support, or Canvas submission occurred. This remains a fictional-scenario coursework design.
