import {useState, useEffect} from "react"

const CLIENTES = {
    pcdf: {
        label: "PCDF",
        ambientes: {
            homologacao: { url: "https://hom.pcdf.gov.br/asi" },
            producao: { url: "https://pcdf.gov.br/asi" },
        },
    },
    tse: {
        label: "TSE",
        ambientes: {
            homologacao: { url: "https://hom.tse.jus.br/asi" },
            producao: { url: "https://tse.jus.br/asi" },
        },
    },
    tcdf: {
        label: "TCDF",
        ambientes: {
            homologacao: { url: "https://hom.tcdf.df.gov.br/asi"}
        },
    },
}

export default function ClientSelector() {
    const [clienteId, setClienteId] = useState("pcdf")
    const [ambienteId, setAmbienteId] = useState("")
    const [url, setUrl] = useState("")
    const [originalUrl, setOriginalUrl] = useState("")
    const [saved, setSaved] = useState(false)

    // Quando o cliente muda, atualiza ambientes e URL
    useEffect(() => {
        const ambientes = Object.keys(CLIENTES[clienteId].ambientes)
        const primeiroAmbiente = ambientes[0]
        setAmbienteId(primeiroAmbiente)
        const novaUrl = CLIENTES[clienteId].ambientes[primeiroAmbiente].url
        setUrl(novaUrl)
        setOriginalUrl(novaUrl)
        setSaved(false)
    }, [clienteId])
    
    // Quando o ambiente muda, atualiza a URL
    useEffect(() => {
        if (!ambienteId) return
        const novaUrl = CLIENTES[clienteId]?.ambientes[ambienteId]?.url ?? ""
        setUrl(novaUrl)
        setOriginalUrl(novaUrl)
        setSaved(false)
    }, [ambienteId])

    function handleSave() {
        setOriginalUrl(url)
        setSaved(true)
        setTimeout(() => setSaved(false), 1500)
    }

    const urlMudou = url !== originalUrl

    return (
        <div className="flex flex-col gap-3">
            
            {/* Clientes */}
            <div className="flex items-center gap-3">
                <label className="text-sm text-gray-500 w-20 text-right">Cliente:</label>
                <select
                    value={clienteId}
                    onChange={(e) => setClienteId(e.target.value)}
                    className="flex-1 border border-gray-200 rounded-md px-3 h-9 text-sm bg-white"
                >
                    {Object.entries(CLIENTES).map(([id, { label }]) => (
                        <option key={id} value={id}>{label}</option>
                    ))}
                </select>
            </div>

            {/* Ambientes */}
            <div className="flex items-center gap-3">
                <label className="text-sm text-gray-500 w-20 text-right">Ambiente:</label>
                <select
                    value={ambienteId}
                    onChange={(e) => setAmbienteId(e.target.value)}
                    className="flex-1 border border-gray-200 rounded-md px-3 h-9 text-sm bg-white"
                >
                    {Object.keys(CLIENTES[clienteId].ambientes).map((amb) => (
                        <option key={amb} value={amb}>{amb.toUpperCase()}</option>
                    ))}
                </select>
            </div>

            {/* URL */}
            <div className="flex items-center gap-3">
                <label className="text-sm text-gray-500 w-20 text-right">URL:</label>
                <div className="flex flex-1 gap-2">
                    <input
                        type="text"
                        value={url}
                        onChange={(e) => { setUrl(e.target.value); setSaved(false) }}
                        className="flex-1 border border-gray-200 rounded-md px-3 h-9 text-sm font-mono bg-white"
                    />
                    {urlMudou && (
                        <button
                            onClick={handleSave}
                            className="px-4 h-9 text-sm border border-gray-200 rounded-md bg-white hover:bg-gray-50"
                        >
                            {saved ? "Salvo!" : "Salvar"}
                        </button>
                    )}
                </div>
            </div>
        </div>
    )
}