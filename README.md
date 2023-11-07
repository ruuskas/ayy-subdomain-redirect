# AYY Subdomain redirects

This repository contains the configuration for redirections of subdomains of ayy.fi and otax.fi.

Formerly associations were able to host their own websites on subdomains of ayy.fi, but this is no longer possible.
To avoid breaking old links, we allow associations to redirect their old subdomains to a new location.

## Adding a new redirect with help from AYY IT

If you want to add a new redirect, but you don't know how to use GitHub, you can ask AYY IT to add the redirect for you.

To do this, send an email to [tietotekniikka@ayy.fi](mailto:tietotekniikka@ayy.fi) with the following information:

- The subdomain you want to redirect from
- The URL you want to redirect to

And optionally:

- Whether you want the path of the original URL to be included in the redirect
- Whether you want the redirect to be permanent

Or you can contact AYY IT through our [customer portal](https://ayyfi.atlassian.net/servicedesk/customer/portal/1).

## Adding a new redirect with a pull request

To add a new redirect, create a new .yml-file in the `subdomains` directory.
The file should be named after your association. For example, if your association is called "Sample association", the file should be named `sample-association.yml`.

The file should contain the following:

```yaml
sample:
  redirect_from: ["sample-association.ayy.fi", "sample-association.otax.fi"]
  redirect_to: "https://sample-association.fi"
  include_path: false
  permanent: false
```

One file can contain multiple redirects, but they should all be for the same association.

The `redirect_from` field should contain a list of the subdomains you want to redirect from.
Only subdomains of ayy.fi and otax.fi are allowed.

The `redirect_to` field should contain the URL you want to redirect to.

The `include_path` field indicates whether the path of the original URL should be included in the redirect.

For example, if `include_path` is `true` and the user visits `https://sample-association.ayy.fi/some-page`, they will be redirected to `https://sample-association.fi/some-page`. If it is `false`, they will be redirected to `https://sample-association.fi`.

The `permanent` field indicates whether the redirect should be [permanent](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/308). If it is `true`, the user's browser will cache the redirect and will not check the original URL again. If it is `false`, the user's browser will check the original URL again the next time they visit the redirect URL.

Once you have created the file, create a pull request to the main repository https://github.com/ayystudentunion/ayy-subdomain-redirect. Once the pull request has been merged, the redirect should be active after a small delay.
