type FooterLink = {
  label: string
  href: string
}

type FooterSectionProps = {
  brand: string
  copyright: string
  links: FooterLink[]
  socialLinks: FooterLink[]
}

export function FooterSection({ brand, copyright, links, socialLinks }: FooterSectionProps) {
  return (
    <footer className="mt-16 border-t border-black/10 pt-8">
      <div className="flex flex-col gap-7 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-neutral-500">{brand}</p>
          <p className="mt-2 max-w-sm text-sm text-neutral-600">{copyright}</p>
        </div>

        <div className="grid gap-7 sm:grid-cols-2">
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-neutral-500">Navigation</p>
            <ul className="space-y-1.5">
              {links.map((link) => (
                <li key={link.label}>
                  <a href={link.href} className="text-sm text-neutral-700 transition hover:text-orange-600">
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-neutral-500">Social</p>
            <ul className="space-y-1.5">
              {socialLinks.map((link) => (
                <li key={link.label}>
                  <a href={link.href} className="text-sm text-neutral-700 transition hover:text-orange-600">
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </footer>
  )
}
