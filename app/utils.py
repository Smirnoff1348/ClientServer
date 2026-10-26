def apply_query(items, args, string_fields=(), numeric_fields=()):
    f = args.get("filter")
    if f:
        f = f.lower()
        items = [x for x in items
                 if any(f in str(getattr(x, k, "")).lower() for k in string_fields)]

    sort = args.get("sort")
    if sort:
        desc = sort.startswith("-")
        field = sort.lstrip("-")
        allowed = set(string_fields) | set(numeric_fields) | {"id"}
        if field in allowed:
            items = sorted(items, key=lambda x: getattr(x, field, ""), reverse=desc)

    limit = args.get("limit", type=int)
    if limit:
        items = items[:limit]

    take = args.get("take", type=int)
    page = args.get("page", type=int, default=1)
    if take and take > 0:
        start = (max(page, 1) - 1) * take
        items = items[start:start + take]

    return items