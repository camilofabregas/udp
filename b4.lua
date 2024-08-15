b4_proto = Proto("B4", "Protocolo RDT Grupo B4 FIUBA")

local vs_messages = {
    [1] = "handshake",
    [2] = "data",
    [3] = "ack",
    [4] = "fin",
}

local vs_commandid = {
    [1] = "download",
    [2] = "upload",
    [3] = "list"
}

local vs_arq = {
    [1] = "Sin configurar",
    [2] = "Stop & Wait",
    [3] = "Selective Repeat"
}

-- declare the fields
local header_message = ProtoField.uint8("b4.message", "Message", base.DEC, vs_messages)
local header_len = ProtoField.uint16("b4.len", "Length", base.DEC)
local handshake_command = ProtoField.uint8("b4.handshake.command", "Client Command", base.DEC, vs_commandid)
local handshake_arq = ProtoField.uint8("b4.handshake.arq", "Arquitectura", base.DEC, vs_arq)
local handshake_error = ProtoField.bool("b4.handshake.error", "Server Error")
local handshake_filesize = ProtoField.uint32("b4.handshake.filesize", "File Size", base.DEC)
local handshake_filename = ProtoField.string("b4.handshake.filename", "File Name")
local data_seq = ProtoField.uint32("b4.data.seq", "Sequence Number", base.DEC)
local data_data = ProtoField.bytes("b4.ack.bytes", "Data Bytes")
local ack_seq = ProtoField.uint32("b4.ack.seq", "Sequence Number", base.DEC)

b4_proto.fields = { 
    header_message, header_len, 
    handshake_command, handshake_error, handshake_arq, handshake_filesize, handshake_filename,
    data_seq, data_data, ack_seq
}

-- create the dissection function
function b4_proto.dissector(buffer, pinfo, tree)

    -- Set the protocol column
    pinfo.cols['protocol'] = "B4"

    -- create the b4 protocol tree item
    local t_b4 = tree:add(b4_proto, buffer())
    local offset = 0
    
    -- Add the header tree item and populate it
    local t_hdr = t_b4:add(buffer(offset, 3), "Header")
    t_hdr:add(header_message, buffer(offset, 1))
    t_hdr:add(header_len, buffer(offset + 1, 2))
    local func_code = buffer(offset, 1):uint()
    local body_len = buffer(offset + 1, 2):uint()
    offset = offset + 3
    
    -- Set the info column to the name of the function
    pinfo.cols['info'] = vs_messages[func_code]
    
    -- dissect handshake
    if func_code == 1 then
      local t_handshake = t_b4:add(buffer(offset, body_len), "Handshake")
      t_handshake:add(handshake_command, buffer(offset, 1))
      offset = offset + 1
      t_handshake:add(handshake_arq, buffer(offset, 1))
      offset = offset + 1
      t_handshake:add(handshake_error, buffer(offset, 1))
      offset = offset + 1
      t_handshake:add(handshake_filesize, buffer(offset, 4))
      offset = offset + 4
      t_handshake:add(handshake_filename, buffer(offset, body_len - 7))
    end
    
    -- dissect data
    if func_code == 2 then
      local t_data = t_b4:add(buffer(offset, body_len), "Data")
      t_data:add(data_seq, buffer(offset, 4))
      offset = offset + 4
      t_data:add(data_data, buffer(offset, body_len - 4))
    end
    -- dissect ack
    if func_code == 3 then
      local t_ack = t_b4:add(buffer(offset, body_len), "Ack")
      t_ack:add(ack_seq, buffer(offset, 4))
    end
    
    -- dissect ack
    if func_code == 4 then
      local t_fin = t_b4:add(buffer(offset, body_len), "Fin")
    end
end

-- load the udp port table
udp_table = DissectorTable.get("udp.port")
-- register the protocol to port 3000
udp_table:add(3000, b4_proto)
