# Example of using semgrep + type checking to ensure sanitization

This example illustrates a technique of using type checking and semgrep to
ensure that a sanitization function is called. This technique may be useful for
legacy projects that don't use automatic sanitization provided by a framework.
Despite the example using Flask, these techniques are recommended for use with
a new Flask project, as it already has built-in HTML sanitization.

Note that this should apply to other languages supported by semgrep and that have a type checker.
Having a stricter type checker can make some of the semgrep rules redundant.

## Migration path

1. Incrementally change each endpoint handling function to output sanitized types, and
   change the type signature accordingly. One can use a "sorry" sanitizer initially. 
   Sorry sanitizers don't actually sanitize, they are just there to satisfy the type checker.
2. Incrementally replace sorry sanitizers. This can be done in tamdem with step 1.
3. Replace the renderer with a wrapped version that requires sanitized types.
   This must be done sequentially after step 1, but can overlap with step 2. This
   ensures all future endpoints only accept sanitized types.
4. Begin breaking builds when the base renderer is used.

## Migration metrics

1. Measure how many endpoints still have unsanitized types in their type signatures.
   Progress can be measured by
   ~~~
   num_sanitized_endpoints / num_endpoints
   ~~~

2. Measure usages of sorry sanitizers. The number of usages may rise even
   though progress is being made, so one would need to look at the
   time-series trend and not judge by the number of sorries at a given point in time.

These metrics can be obtained from semgrep.


## Caveats

Note that this technique will not prevent the combining of literal strings with sanitized strings to create dangerous strings. To mitigate this possibility, one can require that
when combining literal strings with sanitized strings, the output be passed through a blessed 
sanitization function.


## TODO

Turn semgrep output into easily presentable metrics.


## Future

This technique can be extended to include authz policies. See the Rocket framework.
