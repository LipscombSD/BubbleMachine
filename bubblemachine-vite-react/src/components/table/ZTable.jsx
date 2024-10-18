import { useMemo, useState } from 'react';
import {
    MaterialReactTable,
    useMaterialReactTable,
} from 'material-react-table';
import { Box, Button, IconButton, Tooltip } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import useBubbleStore from '../zustand/bubbleStore';

const BubbleTable = () => {
    const [validationErrors, setValidationErrors] = useState({});
    const bubbles = useBubbleStore((state) => state.bubbles);
    const addBubble = useBubbleStore((state) => state.addBubble);
    const updateBubble = useBubbleStore((state) => state.updateBubble);
    const deleteBubble = useBubbleStore((state) => state.deleteBubble);

    const columns = useMemo(
        () => [
            {
                accessorKey: 'id',
                header: 'Id',
                enableEditing: false,
                size: 80,
            },
            {
                accessorKey: 'bubbleName',
                header: 'Bubble Name',
                muiEditTextFieldProps: {
                    required: true,
                    error: !!validationErrors?.bubbleName,
                    helperText: validationErrors?.bubbleName,
                    onFocus: () =>
                        setValidationErrors({
                            ...validationErrors,
                            bubbleName: undefined,
                        }),
                },
            },
            {
                accessorKey: 'startTime',
                header: 'Start Time',
                muiEditTextFieldProps: {
                    required: true,
                    error: !!validationErrors?.startTime,
                    helperText: validationErrors?.startTime,
                    onFocus: () =>
                        setValidationErrors({
                            ...validationErrors,
                            startTime: undefined,
                        }),
                },
            },
            {
                accessorKey: 'stopTime',
                header: 'Stop Time',
                muiEditTextFieldProps: {
                    required: true,
                    error: !!validationErrors?.stopTime,
                    helperText: validationErrors?.stopTime,
                    onFocus: () =>
                        setValidationErrors({
                            ...validationErrors,
                            stopTime: undefined,
                        }),
                },
            },
            {
                accessorKey: 'color',
                header: 'Color',
                editVariant: 'select',
                editSelectOptions: ["Red", "Blue", "Green", "Yellow", "Purple", "Orange", "Pink", "Brown", "Black", "White"],
                muiEditTextFieldProps: {
                    select: true,
                    error: !!validationErrors?.color,
                    helperText: validationErrors?.color,
                },
            },
        ],
        [validationErrors]
    );

    const handleCreateBubble = async ({ values, table }) => {
        const newValidationErrors = validateBubble(values);
        if (Object.values(newValidationErrors).some((error) => error)) {
            setValidationErrors(newValidationErrors);
            return;
        }
        setValidationErrors({});
        addBubble({ ...values, id: (Math.random() + 1).toString(36).substring(7) });
        table.setCreatingRow(null);
    };

    const handleSaveBubble = async ({ values, table }) => {
        const newValidationErrors = validateBubble(values);
        if (Object.values(newValidationErrors).some((error) => error)) {
            setValidationErrors(newValidationErrors);
            return;
        }
        setValidationErrors({});
        console.log('values', values);
        const index = bubbles.findIndex((bubble) => bubble.id === values.id);
        if (index !== -1) {
            updateBubble(index, values);
            console.log('Updated bubble at index:', index);
        } else {
            console.error('Bubble not found:', values.id);
        }
        table.setEditingRow(null);
    };

    const openDeleteConfirmModal = (row) => {
        if (window.confirm('Are you sure you want to delete this bubble?')) {
            const index = bubbles.findIndex((bubble) => bubble.id === row.original.id);
            deleteBubble(index);
        }
    };

    const table = useMaterialReactTable({
        columns,
        data: bubbles,
        createDisplayMode: 'row',
        editDisplayMode: 'row',
        enableEditing: true,
        initialState: { columnVisibility: { id: false } },
        getRowId: (row) => row.id,
        muiToolbarAlertBannerProps: undefined,
        muiTableContainerProps: {
            sx: {
                minHeight: '500px',
            },
        },
        onCreatingRowCancel: () => setValidationErrors({}),
        onCreatingRowSave: handleCreateBubble,
        onEditingRowCancel: () => setValidationErrors({}),
        onEditingRowSave: handleSaveBubble,
        renderRowActions: ({ row, table }) => (
            <Box sx={{ display: 'flex', gap: '1rem' }}>
                <Tooltip title="Edit">
                    <IconButton onClick={() => table.setEditingRow(row)}>
                        <EditIcon />
                    </IconButton>
                </Tooltip>
                <Tooltip title="Delete">
                    <IconButton color="error" onClick={() => openDeleteConfirmModal(row)}>
                        <DeleteIcon />
                    </IconButton>
                </Tooltip>
            </Box>
        ),
        renderTopToolbarCustomActions: ({ table }) => (
            <Button
                variant="contained"
                onClick={() => {
                    table.setCreatingRow(true);
                }}
            >
                Create New Bubble
            </Button>
        ),
        state: {
            isLoading: false,
            isSaving: false,
            showAlertBanner: false,
            showProgressBars: false,
        },
    });

    return <MaterialReactTable table={table} />;
};

export default BubbleTable;

const validateRequired = (value) => String(value).length > 0;
const validateTime = (value) => 
    value !== undefined && 
    value !== null && 
    String(value).length > 0 &&
    String(value).match(/^((0|[1-9][0-9]?)\:)?([0-5][0-9])(:([0-5][0-9]))?$/);

function validateBubble(bubble) {
    return {
        bubbleName: !validateRequired(bubble.bubbleName)
            ? 'Bubble name is Required'
            : '',
        startTime: !validateTime(bubble.startTime) ? 'Start Time is Required' : '',
        stopTime: !validateTime(bubble.stopTime) ? 'Stop Time is Required' : '',        
    };
}