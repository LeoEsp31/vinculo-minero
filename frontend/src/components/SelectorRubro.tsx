import type { Taxonomia } from "../api/tipos";

/** Select de rubros agrupados por familia, con la unidad en que se mide cada uno. */
export function SelectorRubro({
  tax,
  value,
  onChange,
}: {
  tax: Taxonomia;
  value: string;
  onChange: (rubro: string) => void;
}) {
  return (
    <select required value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="" disabled>
        Elegí un rubro…
      </option>
      {Object.entries(tax.familias).map(([fam, nombreFam]) => (
        <optgroup key={fam} label={nombreFam}>
          {tax.rubros
            .filter((r) => r.familia === fam)
            .map((r) => (
              <option key={r.codigo} value={r.codigo}>
                {r.nombre} ({r.unidad})
              </option>
            ))}
        </optgroup>
      ))}
    </select>
  );
}
