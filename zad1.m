function [sol] = zad1(input)
  m_size = size(input)(1);
  
  max_log10 = floor(max(max(log10(input(:,1:m_size)))));
  for i = 1:m_size
    row_max_log10 = floor(max(log10(input(i,1:m_size))));
    input(i,:) = input(i,:) * 10.^(max_log10 - row_max_log10);
  end
  
  cols_perm = eye(m_size + 1);
  for i = 1:m_size
    max_element = max(max(abs(input(i:m_size, i:m_size))));
    [rows_max, cols_max] = find(abs(input(i:m_size, i:m_size)) == max_element);
    row_max = rows_max(1) + i - 1;
    col_max = cols_max(1) + i - 1;
    if (i != row_max)
      % echanging row max with i-th row
      tmp = input(i,:);
      input(i,:) = input(row_max,:);
      input(row_max,:) = tmp;
    end
    if (i != col_max)
      % exchanging col max with i-th col
      tmp = input(:,i);
      input(:,i) = input(:,col_max);
      input(:,col_max) = tmp;
    end
    for j = 1:m_size
      if (j != i)
        for k = (i+1):m_size + 1
          input(j,k) -= (input(j,i) / input(i,i))*input(i,k);
        end
      end
    end
    for j = 1:m_size
      if (j != i)
        input(j,i) = 0;
      end
    end
  end
  for j = 1:m_size 
    input(j, m_size + 1) /= input(j,j);
    input(j,j) = 1;
  end
  sol = input*cols_perm';
end