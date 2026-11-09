# vulnerable-spring

Sample Spring service ("Acme Orders") for the Lightwell Java technical demo.

## Why it is "vulnerable"

`pom.xml` pins libraries Lightwell Java Remediated has rebuilt with CVE fixes, at their **public** versions:

| Library | Public (default build) | Lightwell (`-P lightwell`) |
|---------|------------------------|----------------------------|
| Spring Framework (core, beans, context, aop, expression, web, webmvc, jcl) | `5.3.18` | `5.3.18.rhlw-00010` |
| Spring Boot | `2.7.18` | `2.7.18.rhlw-00004` |
| Spring Security (core, crypto) | `5.7.11` | `5.7.11.rhlw-00006` |
| Logback (classic, core) | `1.2.11` | `1.2.11.rhlw-00001` |
| commons-beanutils | `1.9.4` | `1.9.4.rhlw-00001` |
| Avro | `1.11.0` | `1.11.0.rhlw-00002` |
| jackson-databind | `2.13.4` | `2.13.4.rhlw-00027` |
| XStream | `1.4.18` | `1.4.18.rhlw-00006` |

`OrderService` uses each of them (JSON, SpEL discount rule, bean copy, XML, Avro, URL builder, authorities) and `OrderServiceTest` checks the behavior, so the same tests run on both builds.

Maven versions are exact, so adding a repository is not enough: the `lightwell` profile swaps the version properties and adds the two Lightwell Java feeds (Remediated first, then Validated; Maven Central stays as the last fallback).

## Local (before)

```bash
mvn verify
```

## Lightwell (after)

```bash
export LIGHTWELL_USER='orgId|service-account-name'
export LIGHTWELL_TOKEN='<service account token>'
mvn -s .mvn/lightwell-settings.xml -P lightwell verify
```

If you start the app (`OrdersApplication`) on the Lightwell build, the Spring Boot banner shows `v2.7.18.rhlw-00004`; the tests print it too.

Full demo flow (scan, SBOM, report, provenance check): `scripts/java/scan.sh before|after`, or workflows **J1** / **J2**.
